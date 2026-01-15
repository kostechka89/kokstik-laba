from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
import structlog
from app.api.deps import get_current_user, require_verified_author, resolve_news
from app.db.session import get_db
from app.schemas.news import NewsCreate, NewsRead, NewsUpdate
from app.schemas.comment import CommentRead
from app.crud.news import create_news, list_news, update_news, delete_news
from app.crud.comments import list_comments
from app.services.cache import cache_service
from app.db.models import User, News
from app.workers.tasks import send_news_notification
from app.services.metrics import NEWS_CREATED, NOTIFICATIONS_SENT

router = APIRouter(prefix="/news", tags=["news"])
CACHE_TTL = 300
logger = structlog.get_logger()


def _news_cache_key(news_id: int) -> str:
    return f"news:{news_id}"


@router.get("/", response_model=list[NewsRead])
async def list_all(db: Session = Depends(get_db)):
    cached = cache_service.get_json("news:all")
    if cached:
        logger.info("cache_hit", cache="news", key="news:all")
        return cached
    logger.info("cache_miss", cache="news", key="news:all")
    news_items = await run_in_threadpool(list_news, db)
    data = [NewsRead.model_validate(item).model_dump() for item in news_items]
    cache_service.set_json("news:all", data, CACHE_TTL)
    return news_items


@router.get("/{news_id}", response_model=NewsRead)
async def get_one(news_id: int, db: Session = Depends(get_db)):
    cached = cache_service.get_json(_news_cache_key(news_id))
    if cached:
        logger.info("cache_hit", cache="news", key=_news_cache_key(news_id))
        return cached
    logger.info("cache_miss", cache="news", key=_news_cache_key(news_id))
    news_item = await run_in_threadpool(lambda: db.query(News).filter(News.id == news_id).first())
    if not news_item:
        raise HTTPException(status_code=404, detail="Not found")
    cache_service.set_json(_news_cache_key(news_id), NewsRead.model_validate(news_item).model_dump(), CACHE_TTL)
    return news_item


@router.get("/{news_id}/comments", response_model=list[CommentRead])
async def list_news_comments(news_id: int, db: Session = Depends(get_db)):
    news_item = await run_in_threadpool(lambda: db.query(News).filter(News.id == news_id).first())
    if not news_item:
        raise HTTPException(status_code=404, detail="Not found")
    return await run_in_threadpool(list_comments, db, news_id)


@router.post("/", response_model=NewsRead)
async def create(
    payload: NewsCreate,
    current_user=Depends(require_verified_author),
    db: Session = Depends(get_db),
):
    news_item = await run_in_threadpool(create_news, db, current_user["id"], payload)
    NEWS_CREATED.inc()
    cache_service.delete("news:all")
    users = await run_in_threadpool(lambda: db.query(User).all())
    for user in users:
        key = f"notification:{news_item.id}:{user.id}"
        if cache_service.get_json(key):
            continue
        cache_service.set_json(key, True, ttl=3600)
        try:
            send_news_notification.delay(user.email, news_item.id)
        except Exception:
            pass
        NOTIFICATIONS_SENT.inc()
    return news_item


@router.patch("/{news_id}", response_model=NewsRead)
async def update(
    payload: NewsUpdate,
    current_user=Depends(get_current_user),
    news_item=Depends(resolve_news),
    db: Session = Depends(get_db),
):
    if not (current_user["is_admin"] or news_item.author_id == current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    updated = await run_in_threadpool(update_news, db, news_item, payload)
    cache_service.delete("news:all")
    cache_service.delete(_news_cache_key(news_item.id))
    return updated


@router.delete("/{news_id}")
async def delete(
    current_user=Depends(get_current_user),
    news_item=Depends(resolve_news),
    db: Session = Depends(get_db),
):
    if not (current_user["is_admin"] or news_item.author_id == current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    await run_in_threadpool(delete_news, db, news_item)
    cache_service.delete("news:all")
    cache_service.delete(_news_cache_key(news_item.id))
    return {"status": "deleted"}
