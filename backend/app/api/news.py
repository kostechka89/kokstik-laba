from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_verified_author, resolve_news
from app.db.session import get_db
from app.schemas.news import NewsCreate, NewsRead, NewsUpdate
from app.crud.news import create_news, list_news, update_news, delete_news
from app.services.cache import cache_service
from app.db.models import User, News
from app.workers.tasks import send_news_notification
from app.services.metrics import NEWS_CREATED

router = APIRouter(prefix="/news", tags=["news"])
CACHE_TTL = 300


def _news_cache_key(news_id: int) -> str:
    return f"news:{news_id}"


@router.get("/", response_model=list[NewsRead])
def list_all(db: Session = Depends(get_db)):
    cached = cache_service.get_json("news:all")
    if cached:
        return cached
    news_items = list_news(db)
    data = [NewsRead.model_validate(item).model_dump() for item in news_items]
    cache_service.set_json("news:all", data, CACHE_TTL)
    return news_items


@router.get("/{news_id}", response_model=NewsRead)
def get_one(news_id: int, db: Session = Depends(get_db)):
    cached = cache_service.get_json(_news_cache_key(news_id))
    if cached:
        return cached
    news_item = db.query(News).filter(News.id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="Not found")
    cache_service.set_json(_news_cache_key(news_id), NewsRead.model_validate(news_item).model_dump(), CACHE_TTL)
    return news_item


@router.post("/", response_model=NewsRead)
def create(
    payload: NewsCreate,
    current_user=Depends(require_verified_author),
    db: Session = Depends(get_db),
):
    news_item = create_news(db, current_user["id"], payload)
    NEWS_CREATED.inc()
    cache_service.delete("news:all")
    users = db.query(User).all()
    for user in users:
        key = f"notification:{news_item.id}:{user.id}"
        if cache_service.get_json(key):
            continue
        cache_service.set_json(key, True, ttl=3600)
        try:
            send_news_notification.delay(user.email, news_item.id)
        except Exception:  # noqa: BLE001
            pass
    return news_item


@router.patch("/{news_id}", response_model=NewsRead)
def update(
    payload: NewsUpdate,
    current_user=Depends(get_current_user),
    news_item=Depends(resolve_news),
    db: Session = Depends(get_db),
):
    if not (current_user["is_admin"] or news_item.author_id == current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    updated = update_news(db, news_item, payload)
    cache_service.delete("news:all")
    cache_service.delete(_news_cache_key(news_item.id))
    return updated


@router.delete("/{news_id}")
def delete(
    current_user=Depends(get_current_user),
    news_item=Depends(resolve_news),
    db: Session = Depends(get_db),
):
    if not (current_user["is_admin"] or news_item.author_id == current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    delete_news(db, news_item)
    cache_service.delete("news:all")
    cache_service.delete(_news_cache_key(news_item.id))
    return {"status": "deleted"}
