from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.session import get_db
from app.crud.users import get_user
from app.services.cache import cache_service
from app.db.models import News


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    cached = cache_service.get_json(f"user:{user_id}")
    if cached:
        return cached
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_verified_author": user.is_verified_author,
        "is_admin": user.is_admin,
    }
    cache_service.set_json(f"user:{user_id}", data, ttl=300)
    return data


def require_verified_author(current_user=Depends(get_current_user)):
    if not current_user["is_verified_author"] and not current_user["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not verified")
    return current_user


def require_admin(current_user=Depends(get_current_user)):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not admin")
    return current_user


def resolve_news(news_id: int, db: Session = Depends(get_db)) -> News:
    news_item = db.query(News).filter(News.id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="Not found")
    return news_item
