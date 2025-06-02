from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from src.api import auth
from src.database import engine
from src.api.courses import Course
from src.api.transcripts import get_completed_course_ids
import sqlalchemy
from sqlalchemy import Connection

router = APIRouter(
    prefix="/planner",
    tags=["planner"],
    dependencies=[Depends(auth.get_api_key)],
)

class QuarterPlan(BaseModel):
    quarter_name: str
    courses: List[Course]

class CoursePlan(BaseModel):
    quarters: List[QuarterPlan]
    
def get_planned_courses(connection: Connection, student_id: int) -> list[Course]:
    results = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                    c.id,
                    c.department_code,
                    c.course_number,
                    c.title,
                    c.units,
                    c.gwr,
                    c.uscp,
                    c.notes
                FROM planned_courses pc
                JOIN courses c ON pc.course_id = c.id
                WHERE pc.student_id = :student_id
                """
            ),
            {"student_id": student_id}
        ).mappings().all()

    courses = []
    for row in results:
        course_id = row["id"]
        dept_code = row["department_code"]
        course_number = row["course_number"]
        title = row["title"]
        units = row["units"]
        gwr = row["gwr"]
        uscp = row["uscp"]
        
        course = Course(id=course_id, department_code=dept_code, course_number=course_number, title=title, units=units)
        
        courses.append(course)
    
    return courses
        

@router.get("/create_course_plan")
def create_course_plan(student_id: int = 1):
    with engine.begin() as connection:
        student = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, major_id FROM students WHERE id = :student_id
                """
            ),
            {"student_id": student_id}
        ).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        
        completed_course_ids = get_completed_course_ids(connection=connection, student=student)
        
        planned_courses = get_planned_courses(connection=connection, student_id=student_id)
        
        required_courses = []
        if student.major_id:
            required_courses = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT c.id, c.department_code, c.course_number, c.units, c.title, c.description
                    FROM courses c
                    JOIN major_requirements mr ON c.id = mr.course_id
                    WHERE mr.major_id = :major_id
                    """
                ),
                {"major_id": student.major_id}
            ).fetchall()
        
        remaining_courses = [
            {
                "id": course.id,
                "department_code": course.department_code,
                "course_number": course.course_number,
                "units": course.units,
                "title": course.title,
                "description": course.description
            }
            for course in required_courses 
            if course.id not in completed_course_ids
        ]
        
        quarters = ["Fall 2025", "Winter 2026", "Spring 2026", "Fall 2026"]
        
        quarter_plans = []
        for quarter_name in quarters:
            quarter_courses = [
                {
                    "id": course.id,
                    "department_code": course.department_code,
                    "course_number": course.course_number,
                    "units": course.units,
                    "title": course.title,
                    "description": course.description
                }
                for course in planned_courses 
                if course.planned_quarter == quarter_name
            ]
            
            quarter_plans.append({
                "quarter_name": quarter_name,
                "courses": quarter_courses
            })
        
        current_quarter = 0
        for course in remaining_courses:
            if any(course["id"] in [c["id"] for c in qp["courses"]] for qp in quarter_plans):
                continue
                
            quarter_plans[current_quarter]["courses"].append(course)
            current_quarter = (current_quarter + 1) % len(quarters)
        
        return {"quarters": quarter_plans}

@router.get("/requirements")
def get_requirements(student_id: int = 1):
    with engine.begin() as connection:
        student = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, major_id FROM students WHERE id = :student_id
                """
            ),
            {"student_id": student_id}
        ).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        completed_courses = connection.execute(
            sqlalchemy.text(
                """
                SELECT c.id
                FROM completed_courses cc
                JOIN courses c ON cc.course_id = c.id
                WHERE cc.student_id = :student_id
                """
            ),
            {"student_id": student_id}
        ).fetchall()
        
        completed_course_ids = [row.id for row in completed_courses]
        
        required_courses = []
        if student.major_id:
            required_courses = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT c.id, c.department_code, c.course_number, c.units, c.title, c.description
                    FROM courses c
                    JOIN major_requirements mr ON c.id = mr.course_id
                    WHERE mr.major_id = :major_id
                    """
                ),
                {"major_id": student.major_id}
            ).fetchall()
        
        remaining_courses = [
            {
                "id": course.id,
                "department_code": course.department_code,
                "course_number": course.course_number,
                "units": course.units,
                "title": course.title,
                "description": course.description
            }
            for course in required_courses 
            if course.id not in completed_course_ids
        ]
        
        return remaining_courses