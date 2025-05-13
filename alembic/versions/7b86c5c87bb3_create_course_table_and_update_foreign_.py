"""Create course table and update foreign key for completed courses table

Revision ID: 7b86c5c87bb3
Revises: 3e5ba263d217
Create Date: 2025-05-06 14:55:57.301944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b86c5c87bb3'
down_revision: Union[str, None] = '3e5ba263d217'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create table: courses
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('department_code', sa.String(length=10), nullable=False),
        sa.Column('course_number', sa.Integer, nullable=False),
        sa.Column('units', sa.Integer, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('GE_area_id', sa.Integer, nullable=True),
        sa.Column('GWR', sa.Boolean, nullable=False, default=False),
        sa.Column('USCP', sa.Boolean, nullable=False, default=False),
        sa.Column('term_id', sa.Integer, nullable=True),
    )

    # Create a self-referential foreign key constraint
    op.create_foreign_key('fk_course_id', 'completed_courses', 'courses', ['course_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_constraint('fk_course_id', 'completed_courses', type_='foreignkey')

    # Drop table: courses
    op.drop_table('courses')