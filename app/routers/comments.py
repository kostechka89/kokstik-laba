from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("", response_model=schemas.CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(payload: schemas.CommentCreate, db: Session = Depends(get_db)):
    news = db.get(models.News, payload.news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    author = db.get(models.User, payload.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    comment = models.Comment(
        text=payload.text,
        news_id=payload.news_id,
        author_id=payload.author_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("", response_model=list[schemas.CommentRead])
def list_comments(db: Session = Depends(get_db)):
    return db.query(models.Comment).order_by(models.Comment.id).all()


@router.get("/{comment_id}", response_model=schemas.CommentRead)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.get(models.Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.put("/{comment_id}", response_model=schemas.CommentRead)
def update_comment(
    comment_id: int, payload: schemas.CommentUpdate, db: Session = Depends(get_db)
):
    comment = db.get(models.Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(comment, key, value)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.get(models.Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
    return None
