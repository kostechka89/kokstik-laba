from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    verified_author = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String(1024), nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    hashed_password = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)

    news = relationship(
        "News",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comments = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(JSONB, nullable=False)
    cover_url = Column(String(1024), nullable=True)
    published_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author = relationship("User", back_populates="news")

    comments = relationship(
        "Comment",
        back_populates="news",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    news_id = Column(
        Integer,
        ForeignKey("news.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    news = relationship("News", back_populates="comments")
    author = relationship("User", back_populates="comments")