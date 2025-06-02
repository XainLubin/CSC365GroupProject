from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from src.api import auth
import sqlalchemy as sa
import database as db
from sqlalchemy import Connection
from src.api.courses import Course
from src.api.students import Student
from src.api.transcripts import get_completed_course_ids
from collections import defaultdict

router = APIRouter(
    prefix="/prerequisites",
    tags=["prerequisites"],
    dependencies=[Depends(auth.get_api_key)],
)

class Prerequisite(BaseModel):
    id: int = 0
    course_id: int = 0
    description: str | None = None
    prerequisite_course_ids: dict[int, list[int]] = Field(default_factory=dict)
    ge_prerequisites: list[int] = Field(default_factory=list)
    units: int = 0
    
## Helper functions
def get_ge_prerequisites(connection: Connection, prerequisite_id: int) -> list[int]:
    query = """
        SELECT ge_area_id
        FROM ge_prerequisites
        WHERE prerequisite_id = :id
    """
    results = connection.execute(sa.text(query), {"id": prerequisite_id}).mappings().all()
    return [row['ge_area_id'] for row in results]


def get_prerequisite_ids(connection: Connection, course: Course) -> list[int]:
    query = """
        SELECT prerequisite_id
        FROM course_prerequisites
        WHERE course_id = :id
    """
    results = connection.execute(sa.text(query), {"id": course.id}).mappings().all()
    return [row['prerequisite_id'] for row in results]


def get_prerequisite_courses(connection: Connection, prerequisite_id: int) -> dict[int, int]:
    query = """
        SELECT prerequisite_course_id
        FROM prerequisite_courses
        WHERE prerequisite_id = :id
    """
    results = connection.execute(sa.text(query), {"id": prerequisite_id}).mappings().all()
    return {prerequisite_id: [row['prerequisite_course_id'] for row in results]}


def get_prerequisite_description(connection: Connection, prerequisite_id: int) -> str:
    query = """
        SELECT prerequisite
        FROM prerequisites
        WHERE id = :id
    """
    values = {"id": prerequisite_id}
    result = connection.execute(sa.text(query), values).mappings().one_or_none()
    
    if result is None:
        raise ValueError(f"No prerequisite found with ID {prerequisite_id}")
    
    return result['prerequisite']


def get_degree_requirements(connection: Connection, degree_id: int) -> dict[str, int]:
    query = """
        SELECT *
        FROM degree_requirements
        WHERE degree_id = :id
        """
    values = {"id": degree_id}
    row = connection.execute(sa.text(query), values).mappings().one_or_none()
    
    return dict(row) if row else {}

def get_ge_area_courses(connection: Connection) -> dict[int, list[int]]:
    query = """
        SELECT
            ge_area_id,
            course_id
        FROM ge_area_courses
        WHERE ge_area_id != 0
        ORDER BY ge_area_id ASC, course_id ASC
    """
    result = connection.execute(sa.text(query)).all()
    
    ge_area_courses = defaultdict(list)
    for ge_area_id, course_id in result:
        ge_area_courses[ge_area_id].append(course_id)
    
    return dict(ge_area_courses)
    
def get_prerequisite_units(prerequisite: Prerequisite, requirements: dict[str, int]) -> int:
    units  = 0
    p_id = prerequisite.id
    ge_prereq_ids = {
        1: 'ge_area_a1',
        2: 'ge_area_a2',
        3: 'ge_area_a3',
        4: 'ge_area_b1',
        5: 'ge_area_b2', 
        7: 'ge_area_b4',
        11: 'ge_area_c1',
        12: 'ge_area_c2',
        14: 'ge_area_d2', 
        18: 'ge_area_e'
    }
    
    if p_id == 0:
        # No prerequisites to worry about
        return
    elif p_id in ge_prereq_ids:
        col = ge_prereq_ids[p_id]
        units = requirements[col]
    # If the student has not completed CPE 316
    elif p_id == 17:
        units = 8   
    else:
        units = 4
    
    return units
    
# Returns the student's chosen degree id
def get_degree_id(connection: Connection, student_id: int) -> int:
    query = """
        SELECT degree_id
        FROM students
        WHERE id = :id
        """
    values = {
        "id": student_id
    }
    row = connection.execute(sa.text(query), values).mappings().one_or_none()
    
    if row is None:
        raise ValueError("No degree id found.")

    degree_id = row['degree_id']
    
    return degree_id
    
def build_prerequisites(connection: Connection, course_id: int, prerequisite_ids: list[int], student_id: int) -> list[Prerequisite]:
    prerequisites = []
    # iterate through our prerequisite ids
    if prerequisite_ids:
        for p_id in prerequisite_ids:
            # Get our degree id
            degree_id = get_degree_id(connection=connection, student_id=student_id)
            # If id <= 18: these are ge area related prerequisites
            if p_id < 0:
                raise ValueError("Prerequisite id cannot be negative!")
            elif p_id == 0:
                # No prerequisites so nothing to do
                return []
            else:   # Course has prerequisites
                # Get the ge prerequisites for this course if any
                ge_prerequisites = get_ge_prerequisites(connection=connection, prerequisite_id=p_id)
                # Get the prerequisite courses for this course
                prereq_courses = get_prerequisite_courses(connection=connection, course_id=course_id)
                # Get the description of the prerequisite for user readability to return if prerequisites have not been met
                description = get_prerequisite_description(connection=connection, prerequisite_id=p_id)
                # Get the degree requirements
                requirements = get_degree_requirements(connection=connection, degree_id=degree_id)
                # Get student's completed courses
                completed_courses = get_completed_course_ids(connection=connection, student_id=student_id)
                # Create our prerequisite from the information retrieved above
                if p_id == 46:
                    
                    prereq_courses = {
                        1: prereq_courses[:1],
                        2: prereq_courses[2:]
                    }
                elif p_id == 49:
                    
                    prereq_courses = {
                        1: [103],
                        2: [54, 100],
                        3: [55, 101],
                        4: [212]
                    }
                    
                prereq = Prerequisite(id=p_id, course_id=course_id, description=description, prerequisite_course_ids=prereq_courses, ge_prerequisites=ge_prerequisites)
                    
                # get how many units is necessary for this prerequisite
                prereq_units = get_prerequisite_units(prerequisite=prereq, requirements=requirements)
                prereq.units = prereq_units
                
                prerequisites.append(prereq)
                            
    return prerequisites

    
@router.get("/prerequisites/{course_id}", response_model=list[Prerequisite])
def get_course_prerequisites(student_id: int, course_id: int) -> list[Prerequisite]:
    # Establish connection
    with db.engine.begin() as connection:
        # Get all prerequisites for this course from course_prerequisites table
        prerequisite_ids = get_prerequisite_ids(connection=connection, course=course_id)
        
        if not prerequisite_ids or prerequisite_ids[0] == 0:
            return []
        
        # Build our list of prerequisites for this course
        course_prerequisites = build_prerequisites(connection=connection, course=course_id, prerequisite_ids=prerequisite_ids, student=student_id)
        
    return course_prerequisites