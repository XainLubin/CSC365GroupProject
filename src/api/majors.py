from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from src.api import auth
from src.database import engine
import sqlalchemy
from sqlalchemy import text

router = APIRouter(
    prefix="/majors",
    tags=["majors"],
    dependencies=[Depends(auth.get_api_key)],
)

class MajorBase(BaseModel):
    name: str
    description: Optional[str] = None

class Major(MajorBase):
    id: int

@router.get("/")
def get_majors():
    """
    Get all majors.
    """
    with engine.begin() as connection:
        majors = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name, description FROM majors
                """
            )
        ).fetchall()
        
        return [
            {
                "id": major.id,
                "name": major.name,
                "description": major.description
            } for major in majors
        ]

@router.get("/{major_id}")
def get_major(major_id: int):
    """
    Get a specific major by ID.
    """
    with engine.begin() as connection:
        major = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name, description FROM majors WHERE id = :major_id
                """
            ),
            {"major_id": major_id}
        ).first()
        
        if not major:
            raise HTTPException(status_code=404, detail="Major not found")
        
        return {
            "id": major.id,
            "name": major.name,
            "description": major.description
        }

@router.get("/{major_id}/students")
def get_major_students(major_id: int):
    """
    Get all students in a specific major.
    """
    with engine.begin() as connection:
        major = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM majors WHERE id = :major_id
                """
            ),
            {"major_id": major_id}
        ).first()
        
        if not major:
            raise HTTPException(status_code=404, detail="Major not found")
        
        students = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, first_name, last_name, email
                FROM students
                WHERE major_id = :major_id
                """
            ),
            {"major_id": major_id}
        ).fetchall()
        
        return [
            {
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email
            } for student in students
        ]