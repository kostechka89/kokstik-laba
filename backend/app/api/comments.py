from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.crud.comments import create_comment, update_comment, delete_comment
from app.db.models import Comment

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentRead)
def create(
    payload: CommentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = create_comment(db, current_user["id"], payload)
    return comment


@router.patch("/{comment_id}", response_model=CommentRead)
def update(
    comment_id: int,
    payload: CommentUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Not found")
    if not (current_user["is_admin"] or comment.author_id == current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return update_comment(db, comment, payload)


@router.delete("/{comment_id}")
def delete(
    comment_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Not found")
    if not (current_user["is_admin"] or comment.author_id == current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    delete_comment(db, comment)
    return {"status": "deleted"}
