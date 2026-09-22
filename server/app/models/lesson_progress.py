"""
LessonProgress model.

Tracks how far a student got in a specific lesson, within a specific
enrollment. This is what powers:
 - "resume from where you left off" (watched_seconds)
 - the overall course progress bar (count completed=True rows / total lessons)

UniqueConstraint prevents duplicate progress rows for the same
enrollment+lesson pair - we always UPDATE the existing row, never insert
a second one.
"""

from sqlalchemy import (
    Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("enrollment_id", "lesson_id", name="uq_enrollment_lesson"),
    )

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)

    watched_seconds = Column(Integer, default=0)  # last watched position
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    enrollment = relationship("Enrollment", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress_entries")
