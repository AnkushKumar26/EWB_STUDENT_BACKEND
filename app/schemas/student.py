"""
Pydantic schemas used for request validation and response serialization.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    major: Optional[str] = None
    year: Optional[int] = None
    enrolled_course: Optional[str] = None
    gpa: Optional[float] = None


class StudentCreate(StudentBase):
    """Fields required to create a student."""

    pass


class StudentUpdate(BaseModel):
    """All fields optional -- only send what you want to change."""

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    major: Optional[str] = None
    year: Optional[int] = None
    enrolled_course: Optional[str] = None
    gpa: Optional[float] = None


class StudentRead(StudentBase):
    """What we return to clients -- includes the DB-generated id."""

    id: int

    model_config = ConfigDict(from_attributes=True)
