from fastapi import FastAPI
from src.api import hi, auth
from starlette.middleware.cors import CORSMiddleware

description = """
Course Filer is our Group project which helps students find courses that fit their schedule.
"""
tags_metadata = [
    {"name": "hi", "description": "Place potion orders."},
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
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(hi.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Course Finder!"}
