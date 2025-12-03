import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user
from ..cache import cache_client
from ..tasks import notify_new_news

router = APIRouter(prefix="/news", tags=["news"])
logger = logging.getLogger(__name__)
CACHE_TTL = 300


def _ensure_can_modify(news: models.News, user: models.User):
    if user.role == models.UserRole.admin:
        return
    if news.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot modify this news")


@router.post("/", response_model=schemas.NewsOut, status_code=status.HTTP_201_CREATED)
def create_news(news: schemas.NewsCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_verified_author and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not verified as author")
    if news.author_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create news for another user")
    db_news = models.News(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    cache_client.set_json(f"news:{db_news.id}", schemas.NewsOut.from_orm(db_news).dict(), CACHE_TTL)
    try:
        notify_new_news.delay(db_news.id)
    except Exception:
        logger.warning("Celery broker unavailable; notification skipped")
    return db_news


@router.get("/", response_model=list[schemas.NewsOut])
def list_news(db: Session = Depends(get_db)):
    cached = cache_client.get_json("news:list")
    if cached:
        logger.info("news list served from cache")
        return cached
    news_items = db.query(models.News).all()
    data = [schemas.NewsOut.from_orm(item).dict() for item in news_items]
    cache_client.set_json("news:list", data, CACHE_TTL)
    return news_items


@router.get("/{news_id}", response_model=schemas.NewsOut)
def get_news(news_id: int, db: Session = Depends(get_db)):
    cached = cache_client.get_json(f"news:{news_id}")
    if cached:
        logger.info("news %s served from cache", news_id)
        return cached
    news = db.query(models.News).get(news_id)
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    payload = schemas.NewsOut.from_orm(news).dict()
    cache_client.set_json(f"news:{news_id}", payload, CACHE_TTL)
    return news


@router.put("/{news_id}", response_model=schemas.NewsOut)
def update_news(news_id: int, news_update: schemas.NewsUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    news = db.query(models.News).get(news_id)
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    _ensure_can_modify(news, current_user)
    for field, value in news_update.dict(exclude_unset=True).items():
        setattr(news, field, value)
    db.commit()
    db.refresh(news)
    payload = schemas.NewsOut.from_orm(news).dict()
    cache_client.set_json(f"news:{news.id}", payload, CACHE_TTL)
    cache_client.delete("news:list")
    return news


@router.delete("/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    news = db.query(models.News).get(news_id)
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    _ensure_can_modify(news, current_user)
    db.delete(news)
    db.commit()
    cache_client.delete(f"news:{news_id}")
    cache_client.delete("news:list")
    return {"status": "deleted"}
