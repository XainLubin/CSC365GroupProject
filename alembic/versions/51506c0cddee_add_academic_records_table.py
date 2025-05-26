"""add academic records_table

Revision ID: 51506c0cddee
Revises: dabf8a344a31
Create Date: 2025-05-25 12:47:15.118177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51506c0cddee'
down_revision: Union[str, None] = 'dabf8a344a31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE academic_records (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            overall_gpa DECIMAL(4,3) NOT NULL,
            major_gpa DECIMAL(4,3) NOT NULL,
            total_units_completed INTEGER NOT NULL,
            major_units_completed INTEGER NOT NULL,
            academic_standing VARCHAR(100) NOT NULL,
            quarters_completed INTEGER NOT NULL,
            calculation_date TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('academic_records')