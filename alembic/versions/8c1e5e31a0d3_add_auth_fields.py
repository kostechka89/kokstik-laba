"""add authentication fields to users"""

from alembic import op
import sqlalchemy as sa

revision = '8c1e5e31a0d3'
down_revision = '7eb9224d66e1'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'hashed_password')