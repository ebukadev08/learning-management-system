"""
Pydantic schemas for Course.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.course import DifficultyLevel


class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.beginner
    thumbnail_url: Optional[str] = None
    price: float = 0.0


class CourseUpdate(BaseModel):
    # All optional - client only sends the fields they're changing
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    thumbnail_url: Optional[str] = None
    price: Optional[float] = None


class CourseOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: Optional[str]
    difficulty: DifficultyLevel
    thumbnail_url: Optional[str]
    price: float
    instructor_id: int
    created_at: datetime

    class Config:
        from_attributes = True