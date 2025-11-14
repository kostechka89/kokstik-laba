from datetime import datetime, timedelta
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from fastapi_sso.sso.github import GithubSSO
from jose import JWTError
from app.core.config import get_settings
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.redis_client import redis_client
from app.services.deps import get_db, get_user_repo, get_current_user
from app.schemas.schemas import UserCreate, LoginRequest, TokenOut, SessionOut, UserOut
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()

github_sso = GithubSSO(
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    redirect_uri=settings.GITHUB_REDIRECT_URI,
)


def store_session(user_id: int, jti: str, user_agent: str, expires_at: datetime) -> None:
    if redis_client is None:
        return
    session_data = {
        "user_id": user_id,
        "user_agent": user_agent,
        "expires_at": expires_at.isoformat(),
    }
    ttl_seconds = int((expires_at - datetime.utcnow()).total_seconds())
    try:
        redis_client.set(f"session:{jti}", json.dumps(session_data), ex=ttl_seconds)
        redis_client.sadd(f"user_sessions:{user_id}", jti)
    except Exception:
        pass


def revoke_session(jti: str, user_id: int) -> None:
    if redis_client is None:
        return
    try:
        redis_client.delete(f"session:{jti}")
        redis_client.srem(f"user_sessions:{user_id}", jti)
    except Exception:
        pass


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    repo = get_user_repo(db)
    existing = repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    hashed = hash_password(payload.password)
    user = repo.create(
        name=payload.name,
        email=payload.email,
        verified_author=payload.verified_author,
        avatar_url=payload.avatar_url,
        hashed_password=hashed,
        is_admin=False,
    )
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        verified_author=user.verified_author,
        avatar_url=user.avatar_url,
        registered_at=user.registered_at,
        is_admin=user.is_admin,
    )


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    repo = get_user_repo(db)
    user = repo.get_by_email(payload.email)
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    access_payload = {
        "sub": str(user.id),
        "is_admin": user.is_admin,
        "verified_author": user.verified_author,
    }
    access_token = create_access_token(access_payload)
    refresh_payload = {"sub": str(user.id)}
    refresh_token, jti = create_refresh_token(refresh_payload)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    user_agent = request.headers.get("user-agent", "")
    store_session(user.id, jti, user_agent, expires_at)
    return TokenOut(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.get("/github")
async def github_login():
    return await github_sso.get_login_redirect()


@router.get("/github/callback", response_model=TokenOut)
async def github_callback(request: Request, db: Session = Depends(get_db)):
    async with github_sso:
        sso_user = await github_sso.verify_and_process(request)
    if not sso_user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not provided by GitHub")
    repo = get_user_repo(db)
    user = repo.get_by_email(sso_user.email)
    if not user:
        user = repo.create(
            name=sso_user.display_name or sso_user.email,
            email=sso_user.email,
            verified_author=False,
            avatar_url=getattr(sso_user, "avatar_url", None) or getattr(sso_user, "picture", None),
            hashed_password=None,
            is_admin=False,
        )
    access_payload = {
        "sub": str(user.id),
        "is_admin": user.is_admin,
        "verified_author": user.verified_author,
    }
    access_token = create_access_token(access_payload)
    refresh_payload = {"sub": str(user.id)}
    refresh_token, jti = create_refresh_token(refresh_payload)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    user_agent = request.headers.get("user-agent", "")
    store_session(user.id, jti, user_agent, expires_at)
    return TokenOut(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=TokenOut)
def refresh(request_data: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    token = request_data.refresh_token
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not user_id or not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id_int = int(user_id)
    if redis_client is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Redis not available")
    session_data = redis_client.get(f"session:{jti}")
    if not session_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")
    revoke_session(jti, user_id_int)
    repo = get_user_repo(db)
    user = repo.get(user_id_int)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    access_payload = {
        "sub": str(user.id),
        "is_admin": user.is_admin,
        "verified_author": user.verified_author,
    }
    access_token = create_access_token(access_payload)
    refresh_payload = {"sub": str(user.id)}
    refresh_token_new, new_jti = create_refresh_token(refresh_payload)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    user_agent = request.headers.get("user-agent", "")
    store_session(user.id, new_jti, user_agent, expires_at)
    return TokenOut(access_token=access_token, refresh_token=refresh_token_new, token_type="bearer")


class LogoutRequest(BaseModel):
    refresh_token: str


@router.post("/logout")
def logout(request_data: LogoutRequest):
    token = request_data.refresh_token
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not user_id or not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id_int = int(user_id)
    revoke_session(jti, user_id_int)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Logged out"})


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(current_user=Depends(get_current_user)):
    user_id = current_user.id
    sessions: list[SessionOut] = []
    if redis_client is None:
        return sessions
    jtis = redis_client.smembers(f"user_sessions:{user_id}") or []
    for jti in jtis:
        data = redis_client.get(f"session:{jti}")
        if not data:
            continue
        try:
            obj = json.loads(data)
            sessions.append(
                SessionOut(
                    session_id=jti,
                    user_agent=obj.get("user_agent", ""),
                    expires_at=datetime.fromisoformat(obj.get("expires_at")),
                )
            )
        except Exception:
            continue
    return sessions