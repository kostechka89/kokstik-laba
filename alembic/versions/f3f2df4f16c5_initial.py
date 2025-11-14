
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | default("None")}
Create Date: ${create_date}

"""

from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa

revision = 'f3f2df4f16c5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('verified_author', sa.Boolean(), nullable=False),
    sa.Column('avatar_url', sa.String(length=1024), nullable=True),
    sa.Column('registered_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('news',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('cover_url', sa.String(length=1024), nullable=True),
    sa.Column('published_at', sa.DateTime(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_news_author_id'), 'news', ['author_id'], unique=False)
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('published_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    sa.Column('news_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_author_id'), 'comments', ['author_id'], unique=False)
    op.create_index(op.f('ix_comments_news_id'), 'comments', ['news_id'], unique=False)
    


def downgrade() -> None:
    op.drop_index(op.f('ix_comments_news_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_author_id'), table_name='comments')
    op.drop_table('comments')
    op.drop_index(op.f('ix_news_author_id'), table_name='news')
    op.drop_table('news')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    