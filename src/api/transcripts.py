from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from src.api import auth
import sqlalchemy as sa
import database as db
from sqlalchemy import Connection
from src.api.courses import Course
from src.api.students import Student
from collections import defaultdict

router = APIRouter(
    prefix="/transcript",
    tags=["transcript"],
    dependencies=[Depends(auth.get_api_key)],
)

class Transcript(BaseModel):
    id: int = 0
    student_id: int = 0
    completed_courses: list[int] = Field(default_factory=list)


def get_completed_course_ids(connection: Connection, student_id: int) -> list[int]:
    query = """
        SELECT cc.course_id
        FROM completed_courses cc
        JOIN transcripts t ON cc.transcript_id = t.id
        JOIN students s ON t.student_id = s.id
        WHERE s.id = :id
        ORDER BY cc.transcript_id ASC, cc.course_id ASC
    """
    results = connection.execute(sa.text(query), {"id": student_id}).mappings().all()
    return [row['course_id'] for row in results]