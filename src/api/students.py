from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from src.api import auth, courses
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
    email: EmailStr
    major_id: Optional[int] = None

class StudentCreate(StudentBase):
    password: str

class Student(StudentBase):
    id: int
def student_from_row(row) -> Student:
    """
    Helper function to convert a database row to a Student model.
    """
    return Student(
        id=row.id,
        first_name=row.first_name,
        last_name=row.last_name,
        email=row.email,
        major_id=row.major_id
    )

class CompletedCourse(BaseModel):
    course_id: int
    grade: Optional[str] = None
    quarter_taken: Optional[str] = None

class PlannedCourse(BaseModel):
    course_id: int
    planned_quarter: Optional[str] = None



@router.post("/students", response_model=Student)
def create_student(student: StudentCreate) -> Student:
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
        
        return student_from_row(result)

@router.post("/login/{email}", response_model=Student)
def login(email: str, password: str) -> Student:
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
            {"email": email, "password": password}
        ).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
         
        return student_from_row(result)

@router.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int) -> Student:
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

    return student_from_row(student)
        
        

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
