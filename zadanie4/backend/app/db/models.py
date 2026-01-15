from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_verified_author = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    avatar = Column(String, nullable=True)

    news = relationship("News", back_populates="author", cascade="all, delete")
    comments = relationship("Comment", back_populates="author", cascade="all, delete")


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(JSON, nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover = Column(String, nullable=True)

    author = relationship("User", back_populates="news")
    comments = relationship("Comment", back_populates="news", cascade="all, delete")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    news = relationship("News", back_populates="comments")
    author = relationship("User", back_populates="comments")
