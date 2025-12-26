"""seed mock data

Revision ID: 002_seed_data
Revises: 001_create_tables
Create Date: 2024-01-01 00:00:01.000000

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002_seed_data"
down_revision = "001_create_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("email", sa.String),
        sa.column("registered_at", sa.DateTime(timezone=True)),
        sa.column("is_verified", sa.Boolean),
        sa.column("avatar_url", sa.String),
    )
    news_table = sa.table(
        "news",
        sa.column("id", sa.Integer),
        sa.column("title", sa.String),
        sa.column("content", sa.JSON),
        sa.column("published_at", sa.DateTime(timezone=True)),
        sa.column("cover_url", sa.String),
        sa.column("author_id", sa.Integer),
    )
    comments_table = sa.table(
        "comments",
        sa.column("id", sa.Integer),
        sa.column("text", sa.Text),
        sa.column("published_at", sa.DateTime(timezone=True)),
        sa.column("news_id", sa.Integer),
        sa.column("author_id", sa.Integer),
    )

    now = datetime.utcnow()

    op.bulk_insert(
        users_table,
        [
            {
                "id": 1,
                "name": "Ivan Petrov",
                "email": "ivan.petrov@example.com",
                "registered_at": now,
                "is_verified": True,
                "avatar_url": "https://example.com/avatars/ivan.png",
            },
            {
                "id": 2,
                "name": "Anna Smirnova",
                "email": "anna.smirnova@example.com",
                "registered_at": now,
                "is_verified": False,
                "avatar_url": "https://example.com/avatars/anna.png",
            },
        ],
    )

    op.bulk_insert(
        news_table,
        [
            {
                "id": 1,
                "title": "First verified news",
                "content": {"blocks": [{"type": "text", "value": "Hello"}]},
                "published_at": now,
                "cover_url": "https://example.com/covers/first.png",
                "author_id": 1,
            }
        ],
    )

    op.bulk_insert(
        comments_table,
        [
            {
                "id": 1,
                "text": "Great start!",
                "published_at": now,
                "news_id": 1,
                "author_id": 2,
            }
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM comments")
    op.execute("DELETE FROM news")
    op.execute("DELETE FROM users")
