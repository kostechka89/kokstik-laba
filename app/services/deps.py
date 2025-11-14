from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.db import DATABASE_URL 
from app.repositories.news_repo import NewsRepository
from app.repositories.comments_repo import CommentRepository
from app.repositories.users_repo import UserRepository

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
import json
from datetime import datetime
from app.core.security import decode_token
from app.core.redis_client import redis_client
from app.models.models import User

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_news_repo(db: Session) -> NewsRepository:
    return NewsRepository(db)


def get_comments_repo(db: Session) -> CommentRepository:
    return CommentRepository(db)


def get_user_repo(db: Session) -> UserRepository:
    return UserRepository(db)


security_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme), db: Session = Depends(get_db)) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id_int = int(user_id)
    cached = None
    if redis_client is not None:
        cached_data = redis_client.get(f"user:{user_id_int}")
        if cached_data:
            try:
                cached = json.loads(cached_data)
            except Exception:
                cached = None
    if cached:
        user = User(
            id=cached["id"],
            name=cached["name"],
            email=cached["email"],
            verified_author=cached["verified_author"],
            avatar_url=cached.get("avatar_url"),
            registered_at=datetime.fromisoformat(cached["registered_at"]),
            hashed_password=None,
            is_admin=cached.get("is_admin", False),
        )
    else:
        repo = get_user_repo(db)
        user = repo.get(user_id_int)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        if redis_client is not None:
            try:
                redis_client.set(
                    f"user:{user.id}",
                    json.dumps({
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "verified_author": user.verified_author,
                        "avatar_url": user.avatar_url,
                        "registered_at": user.registered_at.isoformat(),
                        "is_admin": user.is_admin,
                    }),
                    ex=3600,
                )
            except Exception:
                pass
    return user

def require_verified_author(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.verified_author and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not verified as author")
    return current_user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user