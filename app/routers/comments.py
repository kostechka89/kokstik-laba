from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.dependencies import (
    get_comment_or_404,
    get_current_user,
    require_comment_owner_or_admin,
)

router = APIRouter(
    prefix="/comments", tags=["comments"], dependencies=[Depends(get_current_user)]
)


@router.post("", response_model=schemas.CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    payload: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    news = db.get(models.News, payload.news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    comment = models.Comment(
        text=payload.text,
        news_id=payload.news_id,
        author_id=current_user.id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("", response_model=list[schemas.CommentRead])
def list_comments(db: Session = Depends(get_db)):
    return db.query(models.Comment).order_by(models.Comment.id).all()


@router.get("/{comment_id}", response_model=schemas.CommentRead)
def get_comment(comment: models.Comment = Depends(get_comment_or_404)):
    return comment


@router.put("/{comment_id}", response_model=schemas.CommentRead)
def update_comment(
    payload: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    comment: models.Comment = Depends(require_comment_owner_or_admin),
):
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(comment, key, value)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    db: Session = Depends(get_db),
    comment: models.Comment = Depends(require_comment_owner_or_admin),
):
    db.delete(comment)
    db.commit()
    return None
