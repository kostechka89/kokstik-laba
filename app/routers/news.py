from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/news", tags=["news"])


@router.post("", response_model=schemas.NewsRead, status_code=status.HTTP_201_CREATED)
def create_news(payload: schemas.NewsCreate, db: Session = Depends(get_db)):
    author = db.get(models.User, payload.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if not author.is_verified:
        raise HTTPException(status_code=400, detail="Author is not verified")
    news = models.News(
        title=payload.title,
        content=payload.content,
        cover_url=payload.cover_url,
        author_id=payload.author_id,
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


@router.get("", response_model=list[schemas.NewsRead])
def list_news(db: Session = Depends(get_db)):
    return db.query(models.News).order_by(models.News.id).all()


@router.get("/{news_id}", response_model=schemas.NewsRead)
def get_news(news_id: int, db: Session = Depends(get_db)):
    news = db.get(models.News, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.put("/{news_id}", response_model=schemas.NewsRead)
def update_news(
    news_id: int, payload: schemas.NewsUpdate, db: Session = Depends(get_db)
):
    news = db.get(models.News, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(news, key, value)
    db.commit()
    db.refresh(news)
    return news


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(news_id: int, db: Session = Depends(get_db)):
    news = db.get(models.News, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    db.delete(news)
    db.commit()
    return None
