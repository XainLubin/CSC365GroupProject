"""add api_kes table

Revision ID: dabf8a344a31
Revises: be52df6f06f1
Create Date: 2025-05-25 14:12:06.241992

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dabf8a344a31'
down_revision: Union[str, None] = 'be52df6f06f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
"""
    )
    op.execute(
        """
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    api_key UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expiration TIMESTAMP NOT NULL DEFAULT NOW() + INTERVAL '7 days'
);
"""
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('api_keys')
