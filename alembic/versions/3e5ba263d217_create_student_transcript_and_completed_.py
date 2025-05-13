"""Create student, transcript, and completed course tables

Revision ID: 3e5ba263d217
Revises: 
Create Date: 2025-05-06 14:46:25.767960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e5ba263d217'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
     # Create table: student
    op.create_table(
        'students',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('major_id', sa.Integer, nullable=True),
        sa.Column('email', sa.String(length=100), nullable=False),
    )

    # Create table: transcripts
    op.create_table(
        'transcripts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('student_id', sa.Integer, sa.ForeignKey('students.id'), nullable=False)
    )

    # Create table: completed_courses
    op.create_table(
        'completed_courses',
        sa.Column('transcript_id', sa.Integer, sa.ForeignKey('transcripts.id'), nullable=False),
        sa.Column('course_id', sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint('transcript_id', 'course_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop table: completed_courses
    op.drop_table('completed_courses')

    # Drop table: transcripts
    op.drop_table('transcripts')

    # Drop table: student
    op.drop_table('students')
