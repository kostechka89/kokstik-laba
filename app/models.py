from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .database import Base


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    is_verified_author = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)
    role = Column(String, default=UserRole.user)
    hashed_password = Column(String, nullable=True)

    news = relationship("News", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(JSON, nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover = Column(String, nullable=True)

    author = relationship("User", back_populates="news")
    comments = relationship("Comment", back_populates="news", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow)

    news = relationship("News", back_populates="comments")
    author = relationship("User", back_populates="comments")
