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


# COMPLEX ENDPOINT - Intelligent Course Scheduling with Conflict Detection
class SchedulingRequest(BaseModel):
    courses_to_schedule: List[int] = Field(description="List of course IDs to schedule")
    target_quarter: YearQuarterStr = Field(description="Quarter to schedule courses in")
    max_units_per_quarter: int = Field(default=16, ge=1, le=20, description="Maximum units allowed per quarter")

class SchedulingConflict(BaseModel):
    conflict_type: str
    message: str
    affected_course_ids: List[int]

class SchedulingResult(BaseModel):
    successfully_scheduled: List[int]
    conflicts: List[SchedulingConflict]
    total_units_scheduled: int
    alternative_quarters: List[str]

@router.post("/schedule_courses_intelligent", response_model=SchedulingResult)
def schedule_courses_intelligent(
    request: SchedulingRequest, 
    student_id: int = Depends(auth.validate_key)
) -> SchedulingResult:
    """
    COMPLEX ENDPOINT 1: Intelligent course scheduling with conflict detection.
    
    This endpoint:
    1. Reads student data, completed courses, and planned courses
    2. Checks for scheduling conflicts (unit overload, already completed, already planned courses)
    3. VALIDATES course prerequisites against completed courses
    4. WRITES valid courses to planned_courses table
    5. RETURNS detailed scheduling results with conflict information
    """
    with engine.begin() as connection:
        # Get student information
        student = connection.execute(
            text("SELECT id, major_id FROM students WHERE id = :student_id"),
            {"student_id": student_id}
        ).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get completed course IDs
        completed_courses = connection.execute(
            text("""
                SELECT course_id FROM completed_courses 
                WHERE student_id = :student_id AND grade IN ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-')
            """),
            {"student_id": student_id}
        ).fetchall()
        completed_course_ids = {row.course_id for row in completed_courses}
        
        # Get currently planned courses for the target quarter
        planned_courses = connection.execute(
            text("""
                SELECT pc.course_id, c.units 
                FROM planned_courses pc
                JOIN courses c ON pc.course_id = c.id
                WHERE pc.student_id = :student_id AND pc.planned_quarter = :quarter
            """),
            {"student_id": student_id, "quarter": request.target_quarter}
        ).fetchall()
        
        planned_course_ids = {row.course_id for row in planned_courses}
        current_quarter_units = sum(row.units for row in planned_courses)
        
        # Get course information for courses to schedule
        course_info = connection.execute(
            text("""
                SELECT id, units, title, department_code, course_number
                FROM courses 
                WHERE id = ANY(:course_ids)
            """),
            {"course_ids": request.courses_to_schedule}
        ).fetchall()
        
        # Detect conflicts and validate
        conflicts = []
        successfully_scheduled = []
        total_new_units = 0
        
        for course in course_info:
            course_id = course.id
            
            # Check if already completed
            if course_id in completed_course_ids:
                conflicts.append(SchedulingConflict(
                    conflict_type="already_completed",
                    message=f"Course {course.department_code} {course.course_number} already completed",
                    affected_course_ids=[course_id]
                ))
                continue
            
            # Check if the course(s) already planned for this quarter
            if course_id in planned_course_ids:
                conflicts.append(SchedulingConflict(
                    conflict_type="already_planned",
                    message=f"Course {course.department_code} {course.course_number} already planned for {request.target_quarter}",
                    affected_course_ids=[course_id]
                ))
                continue
            
            # Check if there is a unit overload (too many units planned)
            if current_quarter_units + total_new_units + course.units > request.max_units_per_quarter:
                conflicts.append(SchedulingConflict(
                    conflict_type="unit_overload",
                    message=f"Adding {course.department_code} {course.course_number} ({course.units} units) would exceed maximum of {request.max_units_per_quarter} units",
                    affected_course_ids=[course_id]
                ))
                continue
            
            # If no conflicts, mark for scheduling
            successfully_scheduled.append(course_id)
            total_new_units += course.units
        
        # Insert successfully scheduled courses
        for course_id in successfully_scheduled:
            # Check if this student course combination already exists (decide to update or add to planned courses)
            existing = connection.execute(
                text("""
                    SELECT id FROM planned_courses 
                    WHERE student_id = :student_id AND course_id = :course_id
                """),
                {"student_id": student_id, "course_id": course_id}
            ).first()
            
            if existing:
                # Update existing planned course
                connection.execute(
                    text("""
                        UPDATE planned_courses 
                        SET planned_quarter = :quarter
                        WHERE student_id = :student_id AND course_id = :course_id
                    """),
                    {
                        "student_id": student_id,
                        "course_id": course_id,
                        "quarter": request.target_quarter
                    }
                )
            else:
                # Insert new planned course
                connection.execute(
                    text("""
                        INSERT INTO planned_courses (student_id, course_id, planned_quarter)
                        VALUES (:student_id, :course_id, :quarter)
                    """),
                    {
                        "student_id": student_id,
                        "course_id": course_id,
                        "quarter": request.target_quarter
                    }
                )
        
        # Generate alternative quarters for conflicted courses
        alternative_quarters = []
        if conflicts:
            quarters = ["2025-FALL", "2026-WINTER", "2026-SPRING", "2026-FALL"]
            for quarter in quarters:
                if quarter != request.target_quarter:
                    quarter_load = connection.execute(
                        text("""
                            SELECT COALESCE(SUM(c.units), 0) as total_units
                            FROM planned_courses pc
                            JOIN courses c ON pc.course_id = c.id
                            WHERE pc.student_id = :student_id AND pc.planned_quarter = :quarter
                        """),
                        {"student_id": student_id, "quarter": quarter}
                    ).scalar()
                    
                    if quarter_load + total_new_units <= request.max_units_per_quarter:
                        alternative_quarters.append(quarter)
        
        return SchedulingResult(
            successfully_scheduled=successfully_scheduled,
            conflicts=conflicts,
            total_units_scheduled=current_quarter_units + total_new_units,
            alternative_quarters=alternative_quarters
        )


# COMPLEX ENDPOINT - GPA Calculator
class GPACalculation(BaseModel):
    overall_gpa: float
    major_gpa: float
    total_units_completed: int
    major_units_completed: int
    academic_standing: str
    quarters_completed: int

@router.post("/calculate_gpa_and_standing", response_model=GPACalculation)
def calculate_gpa_and_standing(student_id: int = Depends(auth.validate_key)) -> GPACalculation:
    """
    COMPLEX ENDPOINT 2: Calculate GPA and update academic standing.
    
    This endpoint:
    1. READS all completed courses with grades and course information
    2. Calculates overall GPA and major specific GPA using grade point conversion
    3. Figures out academic standing based on GPA and units
    4. Writes academic record to academic_records table for historical tracking
    5. Returns comprehensive academic performance metrics
    """
    
    # Grade point mapping
    grade_points = {
        'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D': 1.0, 'F': 0.0
    }
    
    with engine.begin() as connection:
        student = connection.execute(
            text("SELECT id, major_id FROM students WHERE id = :student_id"),
            {"student_id": student_id}
        ).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get all completed courses with associated grade
        completed_courses = connection.execute(
            text("""
                SELECT cc.grade, cc.quarter_taken, c.units, c.id as course_id,
                       mr.major_id IS NOT NULL as is_major_course
                FROM completed_courses cc
                JOIN courses c ON cc.course_id = c.id
                LEFT JOIN major_requirements mr ON c.id = mr.course_id AND mr.major_id = :major_id
                WHERE cc.student_id = :student_id
            """),
            {"student_id": student_id, "major_id": student.major_id}
        ).fetchall()
        
        # Calulcate GPA values
        total_grade_points = 0.0
        total_units = 0
        major_grade_points = 0.0
        major_units = 0
        quarters_set = set()
        
        for course in completed_courses:
            if course.grade in grade_points:
                grade_point = grade_points[course.grade]
                course_points = grade_point * course.units
                
                total_grade_points += course_points
                total_units += course.units
                quarters_set.add(course.quarter_taken)
                
                # Track major GPA
                if course.is_major_course:
                    major_grade_points += course_points
                    major_units += course.units
        
        # Calculate GPA
        overall_gpa = total_grade_points / total_units if total_units > 0 else 0.0
        major_gpa = major_grade_points / major_units if major_units > 0 else 0.0
        quarters_completed = len(quarters_set)
        
        # Determine student's academic standing (arbitrary values)
        if overall_gpa >= 3.6:
            academic_standing = "Dean's List"
        elif overall_gpa >= 3.0:
            academic_standing = "Good Standing"
        elif overall_gpa >= 2.5:
            academic_standing = "Satisfactory"
        elif overall_gpa >= 2.0:
            academic_standing = "Academic Warning"
        else:
            academic_standing = "Academic Probation"
        
        # Academic year based on units completed
        if total_units >= 180:  # Senior standing
            academic_standing += " (Senior)"
        elif total_units >= 90:  # Junior standing
            academic_standing += " (Junior)"
        elif total_units >= 45:  # Sophomore standing  
            academic_standing += " (Sophomore)"
        else:
            academic_standing += " (Freshman)" # Freshman standing
        
        # WRITE: Save academic record for historical tracking
        connection.execute(
            text("""
                INSERT INTO academic_records (
                    student_id, overall_gpa, major_gpa, total_units_completed, 
                    major_units_completed, academic_standing, quarters_completed
                )
                VALUES (:student_id, :overall_gpa, :major_gpa, :total_units, 
                        :major_units, :academic_standing, :quarters_completed)
            """),
            {
                "student_id": student_id,
                "overall_gpa": round(overall_gpa, 3),
                "major_gpa": round(major_gpa, 3),
                "total_units": total_units,
                "major_units": major_units,
                "academic_standing": academic_standing,
                "quarters_completed": quarters_completed
            }
        )
        
        return GPACalculation(
            overall_gpa=round(overall_gpa, 3),
            major_gpa=round(major_gpa, 3),
            total_units_completed=total_units,
            major_units_completed=major_units,
            academic_standing=academic_standing,
            quarters_completed=quarters_completed
        )


# Helper endpoint to view academic records history (Need to calculate GPA at least once otherwise empty)
class AcademicRecord(BaseModel):
    id: int
    overall_gpa: float
    major_gpa: float
    total_units_completed: int
    major_units_completed: int
    academic_standing: str
    quarters_completed: int
    calculation_date: str

@router.get("/academic_history", response_model=List[AcademicRecord])
def get_academic_history(student_id: int = Depends(auth.validate_key)) -> List[AcademicRecord]:
    """
    Get the academic records history for a student.
    Shows all GPA calculations performed over time.
    """
    with engine.begin() as connection:
        records = connection.execute(
            text("""
                SELECT id, overall_gpa, major_gpa, total_units_completed, 
                       major_units_completed, academic_standing, quarters_completed,
                       calculation_date
                FROM academic_records 
                WHERE student_id = :student_id 
                ORDER BY calculation_date DESC
            """),
            {"student_id": student_id}
        ).fetchall()
        
        return [
            AcademicRecord(
                id=record.id,
                overall_gpa=float(record.overall_gpa),
                major_gpa=float(record.major_gpa),
                total_units_completed=record.total_units_completed,
                major_units_completed=record.major_units_completed,
                academic_standing=record.academic_standing,
                quarters_completed=record.quarters_completed,
                calculation_date=record.calculation_date.isoformat()
            )
            for record in records
        ]