from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProgressUpdate(BaseModel):
    watch_seconds: int
    completed: Optional[bool] = None

class LessonProgressOut(BaseModel):
    id: int
    lesson_id: int
    completed: bool
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class CourseProgressOut(BaseModel):
    course_id: int
    total_lessons: int
    completed_lessons: int
    percent_complete: float
    course_completed: bool