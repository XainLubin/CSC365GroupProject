from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from pydantic import BaseModel, Field, EmailStr, constr
from enum import Enum
from typing import List, Optional, Annotated
from src.api import auth, courses
from src.database import engine
import sqlalchemy
from sqlalchemy import text
import bcrypt

router = APIRouter(
    prefix="/students",
    tags=["students"],
    dependencies=[],
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


GradeStr = Annotated[str, Field(pattern=r"^(A|A-|B\+|B|B-|C\+|C|C-|D|F|P|NP)$")]
PASSING_GRADES = {"A", "A-", "B+", "B", "B-", "C+", "C", "C-","P"}
FAILING_GRADES = {"D", "F", "NP"}


YearQuarterStr = Annotated[str, Field(pattern=r"^\d{4}-(FALL|WINTER|SPRING|SUMMER)$")]

class CompletedCourse(BaseModel):
    course_id: int
    grade: GradeStr
    quarter_taken: YearQuarterStr
    
    def passed(self) -> bool:
        """ See if the course was passed based on the grade."""
        return self.grade in PASSING_GRADES


def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


@router.post("/create", response_model=Student)
def create_student(student: StudentCreate) -> Student:
    """
    Create a new student.
    """
    # Hash the password before storing it
    hashed_password = hash_password(student.password)
    with engine.begin() as connection: 
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO students (first_name, last_name, email, password, major_id) 
                VALUES (:first_name, :last_name, :email, :password, :major_id) 
                ON CONFLICT (email) DO NOTHING
                RETURNING id, first_name, last_name, email, major_id
                """
            ),
            {
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "password": hashed_password,
                "major_id": student.major_id
            }
        ).first()
        
        return student_from_row(result)



@router.post("/login/{email}", response_model=str)
def login(email: str, password: str):
    """
    Login a student with username and password.
    Returns a access token if successful.
    """ 
    with engine.begin() as connection:
        # For simplicity, we're using email as username
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, password
                FROM students 
                WHERE email = :email;
                """
            ),
            {"email": email, "password": password}
        ).one_or_none()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        if not verify_password(password, result.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        student_id = result.id

        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO api_keys (student_id)
                VALUES (:student_id)
                RETURNING api_key
                """
            ),
            {"student_id": student_id}
        ).first()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate API key"
            )
        api_key = str(result.api_key)
 
    return api_key


@router.get("/get", response_model=Student)
def get_student(student_id: int = Depends(auth.validate_key)) -> Student:
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
def mark_course_completed(course: CompletedCourse, student_id: int = Depends(auth.validate_key)):
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

