"""add mock data"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, String, Boolean, DateTime, JSON
from datetime import datetime

revision = '<7eb9224d66e1>'
down_revision = 'f3f2df4f16c5'
branch_labels = None
depends_on = None


def upgrade():
    users_table = table('users',
        column('id', Integer),
        column('name', String),
        column('email', String),
        column('verified_author', Boolean),
        column('avatar_url', String),
        column('registered_at', DateTime),
    )

    op.bulk_insert(users_table, [
        {
            "id": 1,
            "name": "Mock Author",
            "email": "author@example.com",
            "verified_author": True,
            "avatar_url": "https://example.com/avatar1.png",
            "registered_at": datetime.utcnow(),
        },
        {
            "id": 2,
            "name": "Mock Commenter",
            "email": "commenter@example.com",
            "verified_author": False,
            "avatar_url": "https://example.com/avatar2.png",
            "registered_at": datetime.utcnow(),
        },
    ])

    news_table = table('news',
        column('id', Integer),
        column('title', String),
        column('content', JSON),
        column('published_at', DateTime),
        column('author_id', Integer),
        column('cover_url', String),
    )

    op.bulk_insert(news_table, [
        {
            "id": 1,
            "title": "Mock News Title",
            "content": {"text": "This is a mock news content"},
            "published_at": datetime.utcnow(),
            "author_id": 1,
            "cover_url": "https://example.com/cover.png",
        }
    ])

    comments_table = table('comments',
        column('id', Integer),
        column('text', String),
        column('published_at', DateTime),
        column('author_id', Integer),
        column('news_id', Integer),
    )

    op.bulk_insert(comments_table, [
        {
            "id": 1,
            "text": "This is a mock comment",
            "published_at": datetime.utcnow(),
            "author_id": 2,
            "news_id": 1,
        }
    ])


def downgrade():
    op.execute("DELETE FROM comments")
    op.execute("DELETE FROM news")
    op.execute("DELETE FROM users")