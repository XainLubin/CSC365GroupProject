"""Create tables for Majors, Degrees, and Concentrations

Revision ID: 1e3e01bc64fb
Revises: 2a0c2702cd24
Create Date: 2025-05-06 15:28:29.850834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e3e01bc64fb'
down_revision: Union[str, None] = '2a0c2702cd24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create majors table
    op.create_table(
        'majors',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False)
    )

    # Create degrees table
    op.create_table(
        'degrees',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('major_id', sa.Integer, sa.ForeignKey('majors.id'), nullable=False)
    )

    # Create concentrations table
    op.create_table(
        'concentrations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('degree_id', sa.Integer, sa.ForeignKey('degrees.id'), nullable=False)
    )

    # Create degree_courses table
    op.create_table(
        'degree_courses',
        sa.Column('degree_id', sa.Integer, sa.ForeignKey('degrees.id'), primary_key=True),
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True)
    )

    # Create foreign key constraint for students.major_id
    op.create_foreign_key('fk_students_major_id', 'students', 'majors', ['major_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraint from students
    op.drop_constraint('fk_students_major_id', 'students', type_='foreignkey')

    # Drop degree_courses table
    op.drop_table('degree_courses')

    # Drop concentrations table
    op.drop_table('concentrations')

    # Drop degrees table
    op.drop_table('degrees')

    # Drop majors table
    op.drop_table('majors')
