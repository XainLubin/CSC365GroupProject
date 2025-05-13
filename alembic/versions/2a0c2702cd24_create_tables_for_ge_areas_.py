"""Create tables for GE areas, prerequisites, and terms offered.

Revision ID: 2a0c2702cd24
Revises: 7b86c5c87bb3
Create Date: 2025-05-06 15:20:13.796497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a0c2702cd24'
down_revision: Union[str, None] = '7b86c5c87bb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create table: course_prerequisites
    op.create_table(
        'course_prerequisites',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('description', sa.String(length=255), nullable=False)
    )

    # Create table: prerequisites
    op.create_table(
        'prerequisites',
        sa.Column('prerequisite_id', sa.Integer, nullable=False),
        sa.Column('course_id', sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint('prerequisite_id', 'course_id')
    )

    # Create table: course_terms_offered
    op.create_table(
        'course_terms_offered',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('description', sa.String(length=255), nullable=False)
    )

    # Create table: terms
    op.create_table(
        'terms',
        sa.Column('terms_offered_id', sa.Integer, nullable=False),
        sa.Column('term', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['terms_offered_id'], ['course_terms_offered.id']),
        sa.PrimaryKeyConstraint('terms_offered_id', 'term')
    )

    # Create table: course_GE_areas
    op.create_table(
        'course_GE_areas',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('description', sa.String(length=255), nullable=False)
    )

    # Create table: GE_areas
    op.create_table(
        'GE_areas',
        sa.Column('course_GE_id', sa.Integer, nullable=False),
        sa.Column('area', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['course_GE_id'], ['course_GE_areas.id']),
        sa.PrimaryKeyConstraint('course_GE_id', 'area')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop table: GE_areas
    op.drop_table('GE_areas')

    # Drop table: course_GE_areas
    op.drop_table('course_GE_areas')

    # Drop table: terms
    op.drop_table('terms')

    # Drop table: course_terms_offered
    op.drop_table('course_terms_offered')

    # Drop table: prerequisites
    op.drop_table('prerequisites')

    # Drop table: course_prerequisites
    op.drop_table('course_prerequisites')
