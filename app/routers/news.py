from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/news", tags=["news"])


@router.post("/", response_model=schemas.News, status_code=status.HTTP_201_CREATED)
def create_news(payload: schemas.NewsCreate, db: Session = Depends(get_db)):
    author = db.query(models.User).get(payload.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if not author.is_verified_author:
        raise HTTPException(status_code=403, detail="Author is not verified to publish")
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


@router.get("/", response_model=list[schemas.News])
def list_news(db: Session = Depends(get_db)):
    return db.query(models.News).all()


@router.get("/{news_id}", response_model=schemas.News)
def get_news(news_id: int, db: Session = Depends(get_db)):
    news = db.query(models.News).get(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.patch("/{news_id}", response_model=schemas.News)
def update_news(news_id: int, payload: schemas.NewsUpdate, db: Session = Depends(get_db)):
    news = db.query(models.News).get(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(news, field, value)
    db.commit()
    db.refresh(news)
    return news


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(news_id: int, db: Session = Depends(get_db)):
    news = db.query(models.News).get(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    db.delete(news)
    db.commit()
    return None
