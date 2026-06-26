from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class Role(str, Enum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"


class Language(str, Enum):
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    URDU = "ur"
    ENGLISH = "en"


class StudentProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., pattern=r"^\+91[0-9]{10}$")
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    school: Optional[str] = Field(None, max_length=200)
    grade: int = Field(..., ge=1, le=12)
    preferred_language: Language = Language.ENGLISH
    parental_consent: bool = False

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        return v.strip()[:100]


class StudyQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    subject: Optional[str] = Field(None, max_length=100)
    language: Language = Language.ENGLISH
    topic: Optional[str] = Field(None, max_length=200)

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        return v.strip()[:2000]


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size_bytes: int
    signed_url: str
    expires_in_seconds: int = 3600
