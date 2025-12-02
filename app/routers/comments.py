from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
def create_comment(payload: schemas.CommentCreate, db: Session = Depends(get_db)):
    author = db.query(models.User).get(payload.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    news = db.query(models.News).get(payload.news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    comment = models.Comment(text=payload.text, news_id=payload.news_id, author_id=payload.author_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/", response_model=list[schemas.Comment])
def list_comments(db: Session = Depends(get_db)):
    return db.query(models.Comment).all()


@router.get("/{comment_id}", response_model=schemas.Comment)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.patch("/{comment_id}", response_model=schemas.Comment)
def update_comment(comment_id: int, payload: schemas.CommentUpdate, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(comment, field, value)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
    return None
