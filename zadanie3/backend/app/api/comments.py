from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.crud.comments import create_comment, update_comment, delete_comment, list_by_news_id
from app.db.models import Comment

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/", response_model=list[CommentRead])
async def list_comments(
    news_id: int = Query(...),
    db: Session = Depends(get_db),
):
    return await run_in_threadpool(list_by_news_id, db, news_id)


@router.post("/", response_model=CommentRead)
async def create(
    payload: CommentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = await run_in_threadpool(create_comment, db, current_user["id"], payload)
    return comment


@router.patch("/{comment_id}", response_model=CommentRead)
async def update(
    comment_id: int,
    payload: CommentUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = await run_in_threadpool(lambda: db.query(Comment).filter(Comment.id == comment_id).first())
    if not comment:
        raise HTTPException(status_code=404, detail="Not found")
    if not (current_user["is_admin"] or comment.author_id == current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return await run_in_threadpool(update_comment, db, comment, payload)


@router.delete("/{comment_id}")
async def delete(
    comment_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = await run_in_threadpool(lambda: db.query(Comment).filter(Comment.id == comment_id).first())
    if not comment:
        raise HTTPException(status_code=404, detail="Not found")
    if not (current_user["is_admin"] or comment.author_id == current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    await run_in_threadpool(delete_comment, db, comment)
    return {"status": "deleted"}
