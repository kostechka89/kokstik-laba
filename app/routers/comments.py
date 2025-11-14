from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import json
from sqlalchemy.orm import Session

from app.schemas.schemas import CommentCreate, CommentOut, CommentUpdate
from app.services.deps import get_db, get_comments_repo, get_current_user
from app.models.models import User, News
from app.core.redis_client import redis_client

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(payload: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    news = db.get(News, payload.news_id)
    if not news:
        raise HTTPException(status_code=400, detail="News not found")
    repo = get_comments_repo(db)
    return repo.create(
        news_id=payload.news_id,
        author_id=current_user.id,
        text=payload.text,
    )


@router.get("/", response_model=list[CommentOut])
def list_comments(
    skip: int = 0,
    limit: int = 100,
    news_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = get_comments_repo(db)
    return list(repo.list(skip=skip, limit=limit, news_id=news_id))


@router.get("/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = get_comments_repo(db)
    obj = repo.get(comment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Comment not found")
    return obj


@router.patch("/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int, payload: CommentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    repo = get_comments_repo(db)
    obj = repo.get(comment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Comment not found")
    if obj.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    updated = repo.update(comment_id, **payload.model_dump(exclude_unset=True))
    return updated


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = get_comments_repo(db)
    obj = repo.get(comment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Comment not found")
    if obj.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    ok = repo.delete(comment_id)
    return None