"""Lightly populate database.

Revision ID: be52df6f06f1
Revises: 3cb23b1cd7ca
Create Date: 2025-05-17 15:26:13.242830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be52df6f06f1'
down_revision: Union[str, None] = '3cb23b1cd7ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        INSERT INTO majors (name, description) VALUES
        ('Computer Science', 'Bachelor of Science in Computer Science'),
        ('Software Engineering', 'Bachelor of Science in Software Engineering'),
        ('Computer Engineering', 'Bachelor of Science in Computer Engineering')
    """)

    op.execute("""
        INSERT INTO courses (department_code, course_number, title, units, description) VALUES
        ('CSC', 101, 'Fundamentals of Computer Science I', 4, 'Introduction to programming and problem solving using Python'),
        ('CSC', 202, 'Data Structures', 4, 'Implementation and analysis of fundamental data structures'),
        ('CSC', 203, 'Project-Based Object-Oriented Programming and Design', 4, 'Object-oriented programming and design principles'),
        ('CSC', 225, 'Computer Organization', 4, 'Computer architecture and assembly language programming'),
        ('CSC', 248, 'Discrete Structures', 4, 'Discrete mathematics for computer science'),
        ('CSC', 349, 'Design and Analysis of Algorithms', 4, 'Analysis and design of efficient algorithms'),
        ('CSC', 357, 'Systems Programming', 4, 'Systems programming in C and Unix'),
        ('CSC', 430, 'Programming Languages', 4, 'Study of programming language paradigms and concepts'),
        ('CSC', 445, 'Software Engineering', 4, 'Software development lifecycle and methodologies'),
        ('CSC', 491, 'Senior Project', 2, 'Senior project for Computer Science'), 
        ('CSC', 492, 'Senior Project 2', 2, 'Senior project for Computer Science cont.')
    """)

    op.execute("""
        INSERT INTO major_requirements (major_id, course_id, is_required) VALUES
        (1, 1, true),
        (1, 2, true),
        (1, 3, true), 
        (1, 4, true),
        (1, 5, true),
        (1, 6, true),
        (1, 7, true),
        (1, 8, true),
        (1, 9, true),
        (1, 10, true)
    """)

    op.execute("""
        INSERT INTO students (first_name, last_name, email, password, major_id) VALUES
        ('John', 'Doe', 'jdoe@calpoly.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQN3.8xqKJHy', 1),
        ('Jane', 'Smith', 'jsmith@calpoly.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQN3.8xqKJHy', 1),
        ('Alex', 'Johnson', 'ajohnson@calpoly.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQN3.8xqKJHy', 2)
    """)

    op.execute("""
        INSERT INTO completed_courses (student_id, course_id, grade, quarter_taken) VALUES
        (1, 1, 'A', '2023-FALL'),
        (1, 2, 'B+', '2024-WINTER'),
        (1, 3, 'A-', '2024-WINTER')
    """)

    op.execute("""
        INSERT INTO planned_courses (student_id, course_id, planned_quarter) VALUES
        (2, 4, '2024-SPRING'),
        (2, 5, '2024-SPRING'),
        (2, 6, '2024-FALL')
    """)


def downgrade():
    op.execute("DELETE FROM completed_courses")
    op.execute("DELETE FROM planned_courses")
    op.execute("DELETE FROM students")
    op.execute("DELETE FROM major_requirements")
    op.execute("DELETE FROM courses")
    op.execute("DELETE FROM majors") 