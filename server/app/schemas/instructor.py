"""
Pydantic schemas for the instructor dashboard.
"""

from pydantic import BaseModel
from typing import List, Optional


class CourseSummary(BaseModel):
    course_id: int
    title: str
    enrolled_count: int
    average_rating: float
    total_reviews: int
    completion_rate: float  # % of enrolled students who completed the course


class InstructorDashboardOut(BaseModel):
    total_courses: int
    total_students: int  # unique students across all their courses
    courses: List[CourseSummary]


class EnrolledStudentOut(BaseModel):
    user_id: int
    name: str
    email: str
    enrolled_at: str
    progress_percent: float
    completed: bool