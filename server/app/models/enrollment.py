"""
Enrollment model.

This is the join table between students (users) and courses.
It also tracks overall completion status for that student+course pair.
A UniqueConstraint stops a student enrolling in the same course twice.
"""

from sqlalchemy import (
    Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_enrollment"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    lesson_progress = relationship(
        "LessonProgress", back_populates="enrollment", cascade="all, delete-orphan"
    )
