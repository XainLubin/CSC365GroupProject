from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from src.api import auth
from src.database import engine
import sqlalchemy
from sqlalchemy import text

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
    dependencies=[],
)

class CourseBase(BaseModel):
    department_code: str
    course_number: int
    units: int
    title: str
    description: Optional[str] = None

class Course(CourseBase):
    id: int

def course_from_row(row) -> Course:
    """
    Helper function to convert a database row to a Course model.
    """
    return Course(
        id=row.id,
        department_code=row.department_code,
        course_number=row.course_number,
        title=row.title,
        units=row.units,
        description=row.description
    )
def course_list_from_rows(rows) -> List[Course]:
    """
    Helper function to convert a list of database rows to a list of Course models.
    """
    return [course_from_row(row) for row in rows]


@router.get("/", response_model=List[Course])
def get_courses(skip: int = 0, limit: int = 100) -> List[Course]:
    """
    Get all courses, with optional pagination.
    """
    with engine.begin() as connection:
        courses = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, department_code, course_number, units, title, description 
                FROM courses 
                LIMIT :limit OFFSET :skip
                """
            ),
            {"limit": limit, "skip": skip}
        ).fetchall()
        
        return [
            Course(
                id=course.id,
                department_code=course.department_code,
                course_number=course.course_number,
                units=course.units,
                title=course.title,
                description=course.description
            ) 
            for course in courses
        ]

@router.get("/{course_id}", response_model=Course)
def get_course(course_id: int) -> Course:
    """
    Get a specific course by ID.
    """
    with engine.begin() as connection:
        course = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, department_code, course_number, units, title, description 
                FROM courses 
                WHERE id = :course_id
                """
            ),
            {"course_id": course_id}
        ).first()
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return Course(
            id=course.id,
            department_code=course.department_code,
            course_number=course.course_number,
            units=course.units,
            title=course.title,
            description=course.description
        )


@router.get("/code/{department_code}/{course_number}", response_model=Course)
def get_course_by_code(department_code: str, course_number: int) -> Course:
    """
    Get a specific course by department code and course number.
    """
    with engine.begin() as connection:
        course = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, department_code, course_number, units, title, description 
                FROM courses 
                WHERE department_code = :department_code AND course_number = :course_number
                """
            ),
            {"department_code": department_code, "course_number": course_number}
        ).first()
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return Course(
            id=course.id,
            department_code=course.department_code,
            course_number=course.course_number,
            units=course.units,
            title=course.title,
            description=course.description
        )

