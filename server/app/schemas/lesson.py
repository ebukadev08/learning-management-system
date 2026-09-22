"""
Pydantic schemas for Lesson.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LessonCreate(BaseModel):
    title: str
    video_url: str
    resource_url: Optional[str] = None
    order_index: int = 0
    duration_seconds: int = 0


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    video_url: Optional[str] = None
    resource_url: Optional[str] = None
    order_index: Optional[int] = None
    duration_seconds: Optional[int] = None


class LessonOut(BaseModel):
    id: int
    course_id: int
    title: str
    video_url: str
    resource_url: Optional[str]
    order_index: int
    duration_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True

class LessonPreviewOut(BaseModel):
    id: int
    course_id: int
    title: str
    order_index: int
    duration_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True