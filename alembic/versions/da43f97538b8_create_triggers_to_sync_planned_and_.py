"""Create triggers to sync planned and completed courses.

Revision ID: da43f97538b8
Revises: 7ae2c4347c33
Create Date: 2025-05-28 20:52:18.186024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da43f97538b8'
down_revision: Union[str, None] = '7ae2c4347c33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Function to remove a course from planned_courses when added/updated in completed_courses
    op.execute(
        """
        CREATE OR REPLACE FUNCTION sync_completed_to_planned()
        RETURNS TRIGGER AS $$
        DECLARE
            sid INT;
        BEGIN
            SELECT student_id INTO sid FROM transcripts WHERE id = NEW.transcript_id;
            DELETE FROM planned_courses
            WHERE course_id = NEW.course_id AND student_id = sid;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # Function to restore planned_courses when course is deleted from completed_courses
    op.execute(
        """
        CREATE OR REPLACE FUNCTION restore_planned_from_completed()
        RETURNS TRIGGER AS $$
        DECLARE
            sid INT;
        BEGIN
            SELECT student_id INTO sid FROM transcripts WHERE id = OLD.transcript_id;
            INSERT INTO planned_courses (course_id, student_id)
            VALUES (OLD.course_id, sid)
            ON CONFLICT DO NOTHING;
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    
    # Trigger on INSERT or UPDATE to completed_courses
    op.execute(
        """
        CREATE TRIGGER trg_completed_upsert
        AFTER INSERT OR UPDATE ON completed_courses
        FOR EACH ROW EXECUTE FUNCTION sync_completed_to_planned();
        """
    )

    # Trigger on DELETE from completed_courses
    op.execute(
        """
        CREATE TRIGGER trg_completed_delete
        AFTER DELETE ON completed_courses
        FOR EACH ROW EXECUTE FUNCTION restore_planned_from_completed();
        """
    )

def downgrade() -> None:
    """Downgrade schema."""
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_completed_upsert ON completed_courses;")
    op.execute("DROP TRIGGER IF EXISTS trg_completed_delete ON completed_courses;")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS sync_completed_to_planned();")
    op.execute("DROP FUNCTION IF EXISTS restore_planned_from_completed();")
