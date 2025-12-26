from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.dependencies import (
    get_current_user,
    get_news_or_404,
    require_news_owner_or_admin,
    require_verified_author,
)

router = APIRouter(prefix="/news", tags=["news"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=schemas.NewsRead, status_code=status.HTTP_201_CREATED)
def create_news(
    payload: schemas.NewsCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_verified_author),
):
    news = models.News(
        title=payload.title,
        content=payload.content,
        cover_url=payload.cover_url,
        author_id=current_user.id,
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


@router.get("", response_model=list[schemas.NewsRead])
def list_news(db: Session = Depends(get_db)):
    return db.query(models.News).order_by(models.News.id).all()


@router.get("/{news_id}", response_model=schemas.NewsRead)
def get_news(news: models.News = Depends(get_news_or_404)):
    return news


@router.put("/{news_id}", response_model=schemas.NewsRead)
def update_news(
    payload: schemas.NewsUpdate,
    db: Session = Depends(get_db),
    news: models.News = Depends(require_news_owner_or_admin),
):
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(news, key, value)
    db.commit()
    db.refresh(news)
    return news


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(
    db: Session = Depends(get_db),
    news: models.News = Depends(require_news_owner_or_admin),
):
    db.delete(news)
    db.commit()
    return None
