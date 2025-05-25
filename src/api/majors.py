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
def major_from_row(row) -> Major:
    return Major(
        id=row.id,
        name=row.name,
        description=row.description
    )
def major_list_from_rows(rows) -> List[Major]:
    return [major_from_row(row) for row in rows]

@router.get("/", response_model=List[Major])
def get_majors() -> List[Major]:
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
    return major_list_from_rows(majors)
        

@router.get("/{major_id}", response_model=Major)
def get_major(major_id: int) -> Major:
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
        
    return major_from_row(major)

@router.get("/{major_id}/students", response_model=List[Major])
def get_major_students(major_id: int) -> List[Major]:
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
        
    return major_list_from_rows(students)
