"""Create populated schema

Revision ID: f39d70fedc34
Revises: 51506c0cddee
Create Date: 2025-05-28 20:42:40.801068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f39d70fedc34'
down_revision: Union[str, None] = '51506c0cddee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


tables_and_files = {
    'majors': 'majors.csv',
    'degrees': 'degrees.csv',
    'concentrations': 'concentrations.csv',
    'courses': 'courses.csv',
    'ge_areas': 'ge_areas.csv',
    'ge_area_courses': 'ge_area_courses.csv',
    'prerequisites': 'prerequisites.csv',
    'course_prerequisites': 'course_prerequisites.csv',
    'degree_requirements': 'degree_requirements.csv',
    'degree_courses': 'degree_courses.csv',
    'concentration_courses': 'concentration_courses.csv',
    'course_terms': 'course_terms.csv',
    'technical_electives': 'technical_electives.csv',
    'crosslisted_courses': 'crosslisted_courses.csv',
    'ge_prerequisites': 'ge_prerequisites.csv',
    'prerequisite_courses': 'prerequisite_courses.csv'
}

def upgrade():
    
    # Drop initial tables
    op.drop_table('major_requirements')
    op.drop_table('planned_courses')
    op.drop_table('completed_courses')
    op.drop_table('students')
    op.drop_table('courses')
    op.drop_table('majors') 
    
    # 1. majors
    op.create_table(
        'majors',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False)
    )

    # 2. students
    op.create_table(
        'students',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('first_name', sa.String, nullable=False),
        sa.Column('last_name', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('major_id', sa.Integer, sa.ForeignKey('majors.id'))
    )

    # 3. courses
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('department_code', sa.String, nullable=False),
        sa.Column('course_number', sa.Integer, nullable=False),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('units', sa.Integer, nullable=False),
        sa.Column('gwr', sa.Boolean, default=False),
        sa.Column('uscp', sa.Boolean, default=False),
        sa.Column('notes', sa.String)
    )

    # 4. planned_courses
    op.create_table(
        'planned_courses',
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True),
        sa.Column('student_id', sa.Integer, sa.ForeignKey('students.id'), primary_key=True)
    )

    # 5. transcripts
    op.create_table(
        'transcripts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('student_id', sa.Integer, sa.ForeignKey('students.id'))
    )

    # 6. completed_courses
    op.create_table(
        'completed_courses',
        sa.Column('transcript_id', sa.Integer, sa.ForeignKey('transcripts.id'), primary_key=True),
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True)
    )

    # 7. prerequisites
    op.create_table(
        'prerequisites',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('prerequisite', sa.String, nullable=False)
    )

    # 8. course_prerequisites
    op.create_table(
        'course_prerequisites',
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True),
        sa.Column('prerequisite_id', sa.Integer, sa.ForeignKey('prerequisites.id'), primary_key=True)
    )

    # 9. course_terms
    op.create_table(
        'course_terms',
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True),
        sa.Column('term', sa.String, primary_key=True)
    )

    # 10. degrees
    op.create_table(
        'degrees',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('major_id', sa.Integer, sa.ForeignKey('majors.id'))
    )

    # 11. degree_requirements
    op.create_table(
        'degree_requirements',
        sa.Column('degree_id', sa.Integer, sa.ForeignKey('degrees.id'), primary_key=True),
        sa.Column('major_related_units', sa.Integer),
        sa.Column('concentration_units', sa.Integer),
        sa.Column('tech_elective_units', sa.Integer),
        sa.Column('ge_area_a1', sa.Integer),
        sa.Column('ge_area_a2', sa.Integer),
        sa.Column('ge_area_a3', sa.Integer),
        sa.Column('ge_area_b1', sa.Integer),
        sa.Column('ge_area_b2', sa.Integer),
        sa.Column('ge_area_b4', sa.Integer),
        sa.Column('upper_div_b', sa.Integer),
        sa.Column('ge_area_c1', sa.Integer),
        sa.Column('ge_area_c2', sa.Integer),
        sa.Column('ge_c_elective', sa.Integer),
        sa.Column('upper_div_c', sa.Integer),
        sa.Column('ge_area_d1', sa.Integer),
        sa.Column('ge_area_d2', sa.Integer),
        sa.Column('upper_div_d', sa.Integer),
        sa.Column('ge_area_e', sa.Integer),
        sa.Column('ge_area_f', sa.Integer)
    )

    # 12. concentrations
    op.create_table(
        'concentrations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('degree_id', sa.Integer, sa.ForeignKey('degrees.id'))
    )

    # 13. degree_courses
    op.create_table(
        'degree_courses',
        sa.Column('degree_id', sa.Integer, sa.ForeignKey('degrees.id'), primary_key=True),
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True)
    )

    # 14. concentration_courses
    op.create_table(
        'concentration_courses',
        sa.Column('concentration_id', sa.Integer, sa.ForeignKey('concentrations.id'), primary_key=True),
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True)
    )

    # 15. GE_areas
    op.create_table(
        'ge_areas',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('area', sa.String, nullable=False)
    )

    # 16. GE_area_courses
    op.create_table(
        'ge_area_courses',
        sa.Column('ge_area_id', sa.Integer, sa.ForeignKey('ge_areas.id'), primary_key=True),
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True)
    )

    # 17. technical_electives
    op.create_table(
        'technical_electives',
        sa.Column('concentration_id', sa.Integer, sa.ForeignKey('concentrations.id'), primary_key=True),
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True)
    )

    # 18. crosslisted_courses
    op.create_table(
        'crosslisted_courses',
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True),
        sa.Column('crosslisted_course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True)
    )
    
    # 19. ge_prerequisites
    op.create_table(
        'ge_prerequisites',
        sa.Column('prerequisite_id', sa.Integer, sa.ForeignKey('prerequisites.id'), primary_key=True),
        sa.Column('ge_area_id', sa.Integer, sa.ForeignKey('ge_areas.id'), primary_key=True)
    )

    # 20. prerequisite_courses
    op.create_table(
        'prerequisite_courses',
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True),
        sa.Column('prerequisite_course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True)
    )
    
    populate_tables(table_files=tables_and_files)

def read_csv_as_dicts(filename: str) -> list[dict[str, str]]:
    # Adjust to your actual CSV directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    file_path = os.path.join(project_root, "src", "read_from", filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def populate_tables(table_files: dict[str, str]) -> None:
    """
    For each table name and filename pair, reads the file as a list of dicts
    and inserts the data into the corresponding table using raw SQL via op.execute.
    """
    for table_name, filename in table_files.items():
        rows = read_csv_as_dicts(filename)

        if not rows:
            continue  # skip empty file

        for row in rows:
            columns = ', '.join(row.keys())
            values = ', '.join(format_sql_value(v) for v in row.values())

            insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            op.execute(insert_stmt)


def format_sql_value(value: str) -> str:
    """
    Formats a CSV value for SQL insertion. Adds quotes if it's a string.
    Converts 'TRUE'/'FALSE' to SQL booleans, or leaves numeric values unquoted.
    """
    value = value.strip()
    if value.upper() in {'TRUE', 'FALSE'}:
        return value.upper()
    try:
        float(value)  # works for int or float
        return value
    except ValueError:
        return f"'{value.replace("'", "''")}'"

def downgrade():
    for table in [
        'crosslisted_courses', 'technical_electives', 'GE_area_courses', 'GE_areas',
        'concentration_courses', 'degree_courses', 'concentrations', 'degree_requirements', 'degrees',
        'course_terms', 'course_prerequisites', 'prerequisites', 'completed_courses', 'transcripts',
        'planned_courses', 'courses', 'students', 'majors'
    ]:
        op.drop_table(table)
        
    # Rebuild initial tables
    op.create_table(
        'majors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('department_code', sa.String(), nullable=False),
        sa.Column('course_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('units', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('major_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['major_id'], ['majors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    op.create_table(
        'completed_courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('grade', sa.String(), nullable=True),
        sa.Column('quarter_taken', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'planned_courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('planned_quarter', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'major_requirements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('major_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['major_id'], ['majors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Re-initialize table entries
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

