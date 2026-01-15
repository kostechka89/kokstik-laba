from sqlalchemy.orm import Session
from app.db.models import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


def list_comments(db: Session, news_id: int) -> list[Comment]:
    return (
        db.query(Comment)
        .filter(Comment.news_id == news_id)
        .order_by(Comment.published_at.asc())
        .all()
    )


def create_comment(db: Session, author_id: int, payload: CommentCreate) -> Comment:
    comment = Comment(text=payload.text, news_id=payload.news_id, author_id=author_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def update_comment(db: Session, comment: Comment, payload: CommentUpdate) -> Comment:
    comment.text = payload.text
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment: Comment) -> None:
    db.delete(comment)
    db.commit()


def list_by_news_id(db: Session, news_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.news_id == news_id).all()
