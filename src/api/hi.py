from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/hi",
    tags=["hi"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/")
def hello():
    return {"message": "Hello, World!"}

