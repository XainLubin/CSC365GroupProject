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
    dependencies=[Depends(auth.get_api_key)],
)

class CourseBase(BaseModel):
    department_code: str
    course_number: int
    units: int
    title: str
    description: Optional[str] = None

class Course(CourseBase):
    id: int

@router.get("/")
def get_courses(skip: int = 0, limit: int = 100):
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
            {
                "id": course.id,
                "department_code": course.department_code,
                "course_number": course.course_number,
                "units": course.units,
                "title": course.title,
                "description": course.description
            } for course in courses
        ]

@router.get("/{course_id}")
def get_course(course_id: int):
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
        
        return {
            "id": course.id,
            "department_code": course.department_code,
            "course_number": course.course_number,
            "units": course.units,
            "title": course.title,
            "description": course.description
        }

@router.get("/code/{department_code}/{course_number}")
def get_course_by_code(department_code: str, course_number: int):
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
        
        return {
            "id": course.id,
            "department_code": course.department_code,
            "course_number": course.course_number,
            "units": course.units,
            "title": course.title,
            "description": course.description
        }

@router.get("/major/{major_id}")
def get_major_courses(major_id: int):
    """
    Get all courses required for a specific major.
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
        
        courses = connection.execute(
            sqlalchemy.text(
                """
                SELECT c.id, c.department_code, c.course_number, c.units, c.title, c.description, mr.is_required
                FROM major_requirements mr
                JOIN courses c ON mr.course_id = c.id
                WHERE mr.major_id = :major_id
                """
            ),
            {"major_id": major_id}
        ).fetchall()
        
        return [
            {
                "id": course.id,
                "department_code": course.department_code,
                "course_number": course.course_number,
                "units": course.units,
                "title": course.title,
                "description": course.description,
                "is_required": course.is_required
            } for course in courses
        ]