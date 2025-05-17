from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from src.api import auth
from src.database import engine
import sqlalchemy
from sqlalchemy import text

router = APIRouter(
    prefix="",
    tags=["students"],
    dependencies=[Depends(auth.get_api_key)],
)

class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    major_id: Optional[int] = None

class StudentCreate(StudentBase):
    password: str

class Student(StudentBase):
    id: int

class CompletedCourse(BaseModel):
    course_id: int
    grade: Optional[str] = None
    quarter_taken: Optional[str] = None

class PlannedCourse(BaseModel):
    course_id: int
    planned_quarter: Optional[str] = None

@router.post("/students", response_model=Student)
def create_student(student: StudentCreate):
    """
    Create a new student.
    """
    with engine.begin() as connection:
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM students WHERE email = :email
                """
            ),
            {"email": student.email}
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO students (first_name, last_name, email, password, major_id) 
                VALUES (:first_name, :last_name, :email, :password, :major_id) 
                RETURNING id
                """
            ),
            {
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "password": student.password,
                "major_id": student.major_id
            }
        ).first()
        
        return {
            "id": result.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "email": student.email,
            "major_id": student.major_id
        }

@router.post("/login/{username}")
def login(username: str, password: str):
    """
    Login a student with username and password.
    """
    with engine.begin() as connection:
        # For simplicity, we're using email as username
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, first_name, last_name, email, major_id 
                FROM students 
                WHERE email = :email AND password = :password
                """
            ),
            {"email": username, "password": password}
        ).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        courses = connection.execute(
            sqlalchemy.text(
                """
                SELECT c.id, c.department_code, c.course_number, c.units, c.title, cc.grade, cc.quarter_taken
                FROM completed_courses cc
                JOIN courses c ON cc.course_id = c.id
                WHERE cc.student_id = :student_id
                """
            ),
            {"student_id": result.id}
        ).fetchall()
        
        completed_courses = []
        for course in courses:
            completed_courses.append({
                "id": course.id,
                "department_code": course.department_code,
                "course_number": course.course_number,
                "units": course.units,
                "title": course.title,
                "grade": course.grade,
                "quarter_taken": course.quarter_taken
            })
        
        return {
            "id": result.id, 
            "first_name": result.first_name, 
            "last_name": result.last_name, 
            "email": result.email, 
            "major_id": result.major_id,
            "completed_courses": completed_courses
        }

@router.get("/students/{student_id}")
def get_student(student_id: int):
    """
    Get student details by ID.
    """
    with engine.begin() as connection:
        student = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, first_name, last_name, email, major_id 
                FROM students 
                WHERE id = :student_id
                """
            ),
            {"student_id": student_id}
        ).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        completed_courses = connection.execute(
            sqlalchemy.text(
                """
                SELECT c.id, c.department_code, c.course_number, c.units, c.title, cc.grade, cc.quarter_taken
                FROM completed_courses cc
                JOIN courses c ON cc.course_id = c.id
                WHERE cc.student_id = :student_id
                """
            ),
            {"student_id": student_id}
        ).fetchall()
        
        planned_courses = connection.execute(
            sqlalchemy.text(
                """
                SELECT c.id, c.department_code, c.course_number, c.units, c.title, pc.planned_quarter
                FROM planned_courses pc
                JOIN courses c ON pc.course_id = c.id
                WHERE pc.student_id = :student_id
                """
            ),
            {"student_id": student_id}
        ).fetchall()
        
        return {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "email": student.email,
            "major_id": student.major_id,
            "completed_courses": [
                {
                    "id": course.id,
                    "department_code": course.department_code,
                    "course_number": course.course_number,
                    "units": course.units,
                    "title": course.title,
                    "grade": course.grade,
                    "quarter_taken": course.quarter_taken
                } for course in completed_courses
            ],
            "planned_courses": [
                {
                    "id": course.id,
                    "department_code": course.department_code,
                    "course_number": course.course_number,
                    "units": course.units,
                    "title": course.title,
                    "planned_quarter": course.planned_quarter
                } for course in planned_courses
            ]
        }

@router.post("/mark_course_completed", status_code=status.HTTP_204_NO_CONTENT)
def mark_course_completed(course: CompletedCourse, student_id: int):
    """
    Mark a course as completed with a grade.
    """
    with engine.begin() as connection:
        course_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM courses WHERE id = :course_id
                """
            ),
            {"course_id": course.course_id}
        ).first()
        
        if not course_exists:
            raise HTTPException(status_code=404, detail="Course not found")
        
        student_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM students WHERE id = :student_id
                """
            ),
            {"student_id": student_id}
        ).first()
        
        if not student_exists:
            raise HTTPException(status_code=404, detail="Student not found")
        
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM completed_courses 
                WHERE student_id = :student_id AND course_id = :course_id
                """
            ),
            {"student_id": student_id, "course_id": course.course_id}
        ).first()
        
        if existing:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE completed_courses 
                    SET grade = :grade, quarter_taken = :quarter_taken
                    WHERE student_id = :student_id AND course_id = :course_id
                    """
                ),
                {
                    "student_id": student_id,
                    "course_id": course.course_id,
                    "grade": course.grade,
                    "quarter_taken": course.quarter_taken
                }
            )
        else:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO completed_courses (student_id, course_id, grade, quarter_taken)
                    VALUES (:student_id, :course_id, :grade, :quarter_taken)
                    """
                ),
                {
                    "student_id": student_id,
                    "course_id": course.course_id,
                    "grade": course.grade,
                    "quarter_taken": course.quarter_taken
                }
            )

@router.post("/plan_course", status_code=status.HTTP_204_NO_CONTENT)
def plan_course(course: PlannedCourse, student_id: int):
    """
    Plan a course for a future quarter.
    """
    with engine.begin() as connection:
        course_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM courses WHERE id = :course_id
                """
            ),
            {"course_id": course.course_id}
        ).first()
        
        if not course_exists:
            raise HTTPException(status_code=404, detail="Course not found")
        
        student_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM students WHERE id = :student_id
                """
            ),
            {"student_id": student_id}
        ).first()
        
        if not student_exists:
            raise HTTPException(status_code=404, detail="Student not found")
        
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM planned_courses 
                WHERE student_id = :student_id AND course_id = :course_id
                """
            ),
            {"student_id": student_id, "course_id": course.course_id}
        ).first()
        
        if existing:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE planned_courses 
                    SET planned_quarter = :planned_quarter
                    WHERE student_id = :student_id AND course_id = :course_id
                    """
                ),
                {
                    "student_id": student_id,
                    "course_id": course.course_id,
                    "planned_quarter": course.planned_quarter
                }
            )
        else:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO planned_courses (student_id, course_id, planned_quarter)
                    VALUES (:student_id, :course_id, :planned_quarter)
                    """
                ),
                {
                    "student_id": student_id,
                    "course_id": course.course_id,
                    "planned_quarter": course.planned_quarter
                }
            )