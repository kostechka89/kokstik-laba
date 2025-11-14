from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import json
from app.services.deps import get_current_user, require_verified_author
from app.core.redis_client import redis_client
from sqlalchemy.orm import Session
from app.schemas.schemas import NewsCreate, NewsOut, NewsUpdate
from app.services.deps import get_db, get_news_repo
from app.models.models import User

router = APIRouter(prefix="/news", tags=["news"])

@router.post("/", response_model=NewsOut, status_code=status.HTTP_201_CREATED)
def create_news(payload: NewsCreate, db: Session = Depends(get_db), current_user: User = Depends(require_verified_author)):
    repo = get_news_repo(db)
    news_obj = repo.create(
        title=payload.title,
        content=payload.content,
        author_id=current_user.id,
        cover_url=payload.cover_url,
    )
    if redis_client is not None:
        try:
            redis_client.set(
                f"news:{news_obj.id}",
                json.dumps({
                    "id": news_obj.id,
                    "title": news_obj.title,
                    "content": news_obj.content,
                    "cover_url": news_obj.cover_url,
                    "author_id": news_obj.author_id,
                    "published_at": news_obj.published_at.isoformat(),
                }),
                ex=300,
            )
        except Exception:
            pass
    return news_obj

@router.get("/", response_model=list[NewsOut])
def list_news(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = get_news_repo(db)
    return list(repo.list(skip=skip, limit=limit))

@router.get("/{news_id}", response_model=NewsOut)
def get_news(news_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if redis_client is not None:
        cached = redis_client.get(f"news:{news_id}")
        if cached:
            try:
                data = json.loads(cached)
                return NewsOut(
                    id=data["id"],
                    title=data["title"],
                    content=data["content"],
                    cover_url=data.get("cover_url"),
                    author_id=data["author_id"],
                    published_at=datetime.fromisoformat(data["published_at"]),
                )
            except Exception:
                pass
    repo = get_news_repo(db)
    obj = repo.get(news_id)
    if not obj:
        raise HTTPException(status_code=404, detail="News not found")
    if redis_client is not None:
        try:
            redis_client.set(
                f"news:{obj.id}",
                json.dumps({
                    "id": obj.id,
                    "title": obj.title,
                    "content": obj.content,
                    "cover_url": obj.cover_url,
                    "author_id": obj.author_id,
                    "published_at": obj.published_at.isoformat(),
                }),
                ex=300,
            )
        except Exception:
            pass
    return obj

@router.patch("/{news_id}", response_model=NewsOut)
def update_news(news_id: int, payload: NewsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = get_news_repo(db)
    obj = repo.get(news_id)
    if not obj:
        raise HTTPException(status_code=404, detail="News not found")
    if obj.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    updated = repo.update(news_id, **payload.model_dump(exclude_unset=True))
    if redis_client is not None:
        try:
            redis_client.set(
                f"news:{news_id}",
                json.dumps({
                    "id": updated.id,
                    "title": updated.title,
                    "content": updated.content,
                    "cover_url": updated.cover_url,
                    "author_id": updated.author_id,
                    "published_at": updated.published_at.isoformat(),
                }),
                ex=300,
            )
        except Exception:
            pass
    return updated

@router.put("/{news_id}", response_model=NewsOut)
def replace_news(news_id: int, payload: NewsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = get_news_repo(db)
    obj = repo.get(news_id)
    if not obj:
        raise HTTPException(status_code=404, detail="News not found")
    if obj.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    updated = repo.update(news_id, **payload.model_dump())
    if redis_client is not None:
        try:
            redis_client.set(
                f"news:{news_id}",
                json.dumps({
                    "id": updated.id,
                    "title": updated.title,
                    "content": updated.content,
                    "cover_url": updated.cover_url,
                    "author_id": updated.author_id,
                    "published_at": updated.published_at.isoformat(),
                }),
                ex=300,
            )
        except Exception:
            pass
    return updated

@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(news_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = get_news_repo(db)
    obj = repo.get(news_id)
    if not obj:
        raise HTTPException(status_code=404, detail="News not found")
    if obj.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    ok = repo.delete(news_id)
    if ok and redis_client is not None:
        try:
            redis_client.delete(f"news:{news_id}")
        except Exception:
            pass
    return None