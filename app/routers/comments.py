from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])


def _ensure_can_modify(comment: models.Comment, user: models.User):
    if user.role == models.UserRole.admin:
        return
    if comment.author_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot modify this comment")


@router.post("/", response_model=schemas.CommentOut, status_code=201)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if comment.author_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Cannot create comment for another user")
    db_comment = models.Comment(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.put("/{comment_id}", response_model=schemas.CommentOut)
def update_comment(comment_id: int, update: schemas.CommentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comment = db.query(models.Comment).get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    _ensure_can_modify(comment, current_user)
    for field, value in update.dict(exclude_unset=True).items():
        setattr(comment, field, value)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comment = db.query(models.Comment).get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    _ensure_can_modify(comment, current_user)
    db.delete(comment)
    db.commit()
    return {"status": "deleted"}
