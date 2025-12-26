import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.github import GitHubSSO
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db import get_db
from app.dependencies import get_current_user, get_user_agent

router = APIRouter(prefix="/auth", tags=["auth"])

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "mock-client-id")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "mock-client-secret")
GITHUB_REDIRECT_URI = os.getenv(
    "GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback"
)

github_sso = GitHubSSO(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    redirect_uri=GITHUB_REDIRECT_URI,
)


def issue_tokens(
    user: models.User, db: Session, user_agent: str
) -> schemas.TokenPair:
    access_token = create_access_token(user.id)
    refresh_token, jti, _ = create_refresh_token(user.id)
    session = models.RefreshSession(
        user_id=user.id,
        refresh_jti=jti,
        user_agent=user_agent,
        last_used_at=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    return schemas.TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=schemas.TokenPair)
def register(
    payload: schemas.RegisterRequest,
    db: Session = Depends(get_db),
    user_agent: str = Depends(get_user_agent),
):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        name=payload.name,
        email=payload.email,
        is_verified=False,
        is_admin=False,
        avatar_url=payload.avatar_url,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return issue_tokens(user, db, user_agent)


@router.post("/login", response_model=schemas.TokenPair)
def login(
    payload: schemas.LoginRequest,
    db: Session = Depends(get_db),
    user_agent: str = Depends(get_user_agent),
):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return issue_tokens(user, db, user_agent)


@router.post("/refresh", response_model=schemas.TokenPair)
def refresh_tokens(
    payload: schemas.RefreshRequest,
    db: Session = Depends(get_db),
    user_agent: str = Depends(get_user_agent),
):
    try:
        data = decode_token(payload.refresh_token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    jti = data.get("jti")
    user_id = int(data.get("sub", 0))
    session = (
        db.query(models.RefreshSession)
        .filter(models.RefreshSession.refresh_jti == jti)
        .first()
    )
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=401, detail="Session not found")
    session.last_used_at = datetime.utcnow()
    session.user_agent = user_agent
    db.commit()
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access_token = create_access_token(user.id)
    refresh_token, new_jti, _ = create_refresh_token(user.id)
    session.refresh_jti = new_jti
    db.commit()
    return schemas.TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: schemas.LogoutRequest,
    db: Session = Depends(get_db),
):
    try:
        data = decode_token(payload.refresh_token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    jti = data.get("jti")
    session = (
        db.query(models.RefreshSession)
        .filter(models.RefreshSession.refresh_jti == jti)
        .first()
    )
    if session:
        db.delete(session)
        db.commit()
    return None


@router.get("/sessions", response_model=list[schemas.RefreshSessionRead])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.RefreshSession)
        .filter(models.RefreshSession.user_id == current_user.id)
        .order_by(models.RefreshSession.id)
        .all()
    )


@router.get("/github/login")
async def github_login(request: Request):
    return await github_sso.get_login_redirect(request)


@router.get("/github/callback")
async def github_callback(
    request: Request,
    db: Session = Depends(get_db),
    user_agent: str = Depends(get_user_agent),
):
    github_user = await github_sso.verify_and_process(request)
    if not github_user:
        raise HTTPException(status_code=401, detail="GitHub authentication failed")

    existing = (
        db.query(models.User)
        .filter(models.User.github_id == str(github_user.id))
        .first()
    )
    if not existing:
        email = github_user.email or f"github_{github_user.id}@example.com"
        existing = db.query(models.User).filter(models.User.email == email).first()
        if not existing:
            existing = models.User(
                name=github_user.name or github_user.username or "GitHub User",
                email=email,
                avatar_url=github_user.avatar_url,
                github_id=str(github_user.id),
                is_verified=False,
                is_admin=False,
            )
            db.add(existing)
            db.commit()
            db.refresh(existing)
        else:
            existing.github_id = str(github_user.id)
            db.commit()
    tokens = issue_tokens(existing, db, user_agent)
    redirect_url = os.getenv("FRONTEND_REDIRECT_URL")
    if redirect_url:
        return RedirectResponse(
            url=f"{redirect_url}?access_token={tokens.access_token}&refresh_token={tokens.refresh_token}"
        )
    return tokens
