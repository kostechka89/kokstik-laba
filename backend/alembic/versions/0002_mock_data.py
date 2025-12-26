"""mock data

Revision ID: 0002
Revises: 0001
Create Date: 2024-12-26
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    now = datetime.utcnow()

    users = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("email", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("registered_at", sa.DateTime),
        sa.column("is_verified_author", sa.Boolean),
        sa.column("is_admin", sa.Boolean),
        sa.column("avatar", sa.String),
    )

    # ВАЖНО: фиксируем id, чтобы дальше можно было ссылаться на author_id
    op.bulk_insert(
        users,
        [
            {
                "id": 1,
                "name": "Admin",
                "email": "admin@example.com",
                "hashed_password": None,
                "registered_at": now,
                "is_verified_author": True,
                "is_admin": True,
                "avatar": None,
            },
            {
                "id": 2,
                "name": "Author",
                "email": "author@example.com",
                "hashed_password": None,
                "registered_at": now,
                "is_verified_author": True,
                "is_admin": False,
                "avatar": None,
            },
            {
                "id": 3,
                "name": "Reader",
                "email": "reader@example.com",
                "hashed_password": None,
                "registered_at": now,
                "is_verified_author": False,
                "is_admin": False,
                "avatar": None,
            },
        ],
    )

    news = sa.table(
        "news",
        sa.column("id", sa.Integer),
        sa.column("title", sa.String),
        sa.column("content", sa.JSON),
        sa.column("published_at", sa.DateTime),
        sa.column("author_id", sa.Integer),
        sa.column("cover", sa.String),
    )

    op.bulk_insert(
        news,
        [
            {
                "id": 1,
                "title": "Welcome",
                "content": {"text": "Hello"},
                "published_at": now,
                "author_id": 2,
                "cover": None,
            }
        ],
    )

    comments = sa.table(
        "comments",
        sa.column("id", sa.Integer),
        sa.column("text", sa.String),
        sa.column("published_at", sa.DateTime),
        sa.column("news_id", sa.Integer),
        sa.column("author_id", sa.Integer),
    )

    op.bulk_insert(
        comments,
        [
            {
                "id": 1,
                "text": "Nice",
                "published_at": now,
                "news_id": 1,
                "author_id": 3,
            }
        ],
    )

    # КРИТИЧНО: выравниваем sequence, чтобы следующий insert не конфликтовал
    op.execute(
        "SELECT setval(pg_get_serial_sequence('users','id'), "
        "COALESCE((SELECT MAX(id) FROM users), 1), true);"
    )
    op.execute(
        "SELECT setval(pg_get_serial_sequence('news','id'), "
        "COALESCE((SELECT MAX(id) FROM news), 1), true);"
    )
    op.execute(
        "SELECT setval(pg_get_serial_sequence('comments','id'), "
        "COALESCE((SELECT MAX(id) FROM comments), 1), true);"
    )


def downgrade() -> None:
    op.execute("DELETE FROM comments")
    op.execute("DELETE FROM news")
    op.execute("DELETE FROM users")
