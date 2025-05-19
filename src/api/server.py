from fastapi import FastAPI
from src.api import hi, auth, students, courses, majors, planner
from starlette.middleware.cors import CORSMiddleware

description = """
Course Finder is our Group project which helps students find courses that fit their schedule.
"""
tags_metadata = [
    {"name": "students", "description": "Operations with students."},
    {"name": "courses", "description": "Operations with courses."},
    {"name": "majors", "description": "Operations with majors and degrees."},
    {"name": "planner", "description": "Course plan generation."},
    {"name": "hi", "description": "Hello world test endpoint."},
]

app = FastAPI(
    title="Course Finder",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Spencer Perley",
        "email": "sperley@calpoly.edu",
    },
    openapi_tags=tags_metadata,
)

origins = ["**"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(hi.router)
app.include_router(students.router)
app.include_router(courses.router)
app.include_router(majors.router)
app.include_router(planner.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Course Finder!"}