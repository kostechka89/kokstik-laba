from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.github import GithubSSO
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import create_token, verify_password
from app.crud.users import create_user, get_user, get_user_by_email
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, SessionInfo, Token
from app.schemas.user import UserCreate, UserRead
from app.services.metrics import USERS_CREATED
from app.services.sessions import session_store

router = APIRouter(prefix="/auth", tags=["auth"])


def _github_sso() -> GithubSSO:
    settings = get_settings()
    return GithubSSO(
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
        # Must match GitHub OAuth App "Authorization callback URL"
        redirect_uri="http://localhost:8000/auth/github/callback",
        allow_insecure_http=True,
    )


@router.get("/github")
async def github_login():
    """Start GitHub OAuth flow (browser redirect)."""
    return await _github_sso().get_login_redirect()


@router.get("/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    """GitHub OAuth callback.

    Creates a local user on first login (role: обычный пользователь),
    then issues JWT access/refresh and redirects back to frontend with tokens in query params.
    """
    settings = get_settings()
    sso = _github_sso()

    try:
        gh_user = await sso.verify_and_process(request)
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="GitHub OAuth failed")

    email = getattr(gh_user, "email", None) or (gh_user.get("email") if isinstance(gh_user, dict) else None)
    if not email:
        raise HTTPException(status_code=400, detail="GitHub account has no public email")

    display_name = (
        getattr(gh_user, "display_name", None)
        or getattr(gh_user, "name", None)
        or (gh_user.get("display_name") if isinstance(gh_user, dict) else None)
        or (gh_user.get("name") if isinstance(gh_user, dict) else None)
        or email.split("@")[0]
    )
    avatar = getattr(gh_user, "picture", None) or (gh_user.get("picture") if isinstance(gh_user, dict) else None)

    user = get_user_by_email(db, email)
    if not user:
        import secrets

        user = create_user(
            db,
            UserCreate(
                name=str(display_name),
                email=email,
                password=secrets.token_urlsafe(24),
                avatar=avatar,
                is_verified_author=False,
                is_admin=False,
            ),
        )
        USERS_CREATED.inc()

    session_id = session_store.create(user.id, request.headers.get("user-agent", "unknown"))
    access_token = create_token(str(user.id), timedelta(minutes=settings.access_token_expire_minutes))
    refresh_token = create_token(
        str(user.id),
        timedelta(minutes=settings.refresh_token_expire_minutes),
        extra={"sid": session_id},
    )

    redirect_url = f"{settings.frontend_url}/login?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(url=redirect_url)


@router.post("/register", response_model=UserRead)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # ВАЖНО: если по ТЗ нельзя самому ставить is_admin/is_verified_author — то надо принудительно обнулять тут.
    # Сейчас у тебя по ТЗ допускается автор через is_verified_author? Если нет — скажи, и я сделаю строго.
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    user = create_user(db, payload)
    USERS_CREATED.inc()
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not user.hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    settings = get_settings()
    session_id = session_store.create(user.id, request.headers.get("user-agent", "unknown"))

    access_token = create_token(str(user.id), timedelta(minutes=settings.access_token_expire_minutes))
    refresh_token = create_token(
        str(user.id),
        timedelta(minutes=settings.refresh_token_expire_minutes),
        extra={"sid": session_id},
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest):
    settings = get_settings()
    try:
        claims = jwt.decode(payload.refresh_token, settings.secret_key, algorithms=["HS256"])
        user_id = claims.get("sub")
        session_id = claims.get("sid")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if not session_id or not session_store.get(session_id):
        raise HTTPException(status_code=401, detail="Session not found")

    access_token = create_token(str(user_id), timedelta(minutes=settings.access_token_expire_minutes))
    refresh_token = create_token(
        str(user_id),
        timedelta(minutes=settings.refresh_token_expire_minutes),
        extra={"sid": session_id},
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
def logout(payload: RefreshRequest):
    settings = get_settings()
    try:
        claims = jwt.decode(payload.refresh_token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    session_id = claims.get("sid")
    if session_id:
        session_store.delete(session_id)
    return {"status": "logged_out"}


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Return current user info by access token (always load from DB)."""
    user = get_user(db, current_user["id"])
    if not user:
        # Обычно это случается если ты сделал docker compose down -v (БД новая),
        # а токен остался старый. Код здесь правильный: токен не может ссылаться на несуществующего юзера.
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/sessions", response_model=list[SessionInfo])
def list_sessions(current_user=Depends(get_current_user)):
    return session_store.list_for_user(current_user["id"])
