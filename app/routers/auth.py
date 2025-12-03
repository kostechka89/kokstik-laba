import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import hash_password, verify_password, create_tokens, get_current_user
from ..cache import cache_client
from ..config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = models.User(
        name=payload.name,
        email=payload.email,
        is_verified_author=payload.is_verified_author,
        avatar=payload.avatar,
        role=payload.role,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), user_agent: str | None = Header(default="")):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access, refresh = create_tokens(user)
    session_id = str(uuid.uuid4())
    cache_client.set_session(
        session_id,
        {
            "user_id": user.id,
            "user_agent": user_agent or "",
            "expires_at": (datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_minutes)).isoformat(),
        },
        ttl_seconds=settings.refresh_token_expire_minutes * 60,
    )
    return schemas.Token(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db), user_agent: str | None = Header(default="")):
    # naive refresh: ensure session exists
    session = None
    for key, value in list(cache_client.fallback.items()):
        if key.startswith("session:"):
            data, _ = value
            if data.get("user_agent") == user_agent:
                session = data
                break
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    user = db.query(models.User).get(session["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    access, refresh = create_tokens(user)
    return schemas.Token(access_token=access, refresh_token=refresh)


@router.get("/sessions", response_model=list[schemas.SessionOut])
def my_sessions(current_user: models.User = Depends(get_current_user)):
    sessions: list[schemas.SessionOut] = []
    for key, value in list(cache_client.fallback.items()):
        if key.startswith("session:"):
            data, expire = value
            if data.get("user_id") == current_user.id:
                sessions.append(
                    schemas.SessionOut(
                        session_id=key.split(":", 1)[1],
                        user_agent=data.get("user_agent", ""),
                        user_id=current_user.id,
                        expires_at=expire,
                    )
                )
    return sessions


@router.post("/logout")
def logout(session_id: str):
    cache_client.delete_session(session_id)
    return {"status": "logged_out"}
