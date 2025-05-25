from src import config
from fastapi import Security, HTTPException, status, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi import APIRouter, Depends, HTTPException, status, Form, Body, Response
from pydantic import BaseModel, Field, EmailStr, constr
from enum import Enum
from typing import List, Optional, Annotated
from src.database import engine
import sqlalchemy


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[],
)

api_key_header = APIKeyHeader(name="access_token", auto_error=False)


async def validate_key(request: Request, api_key_header: str = Security(api_key_header)) -> int:
    """
    Validate user credentials against the database.
    """
    with engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT student_id
                FROM api_keys
                WHERE api_key = :api_key
                AND expiration > NOW()
                """
            ),
            {"api_key": api_key_header}
        ).one_or_none()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key or expired, please log in again."
            )
        
        return result.student_id

