"""
Lesson model.

`order_index` defines the sequence lessons appear/must be watched in.
Duration is stored in seconds - easier to do math with than "12:34" strings.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    title = Column(String(200), nullable=False)
    video_url = Column(String(500), nullable=False)
    resource_url = Column(String(500), nullable=True)  # downloadable PDF/notes etc
    order_index = Column(Integer, nullable=False, default=0)
    duration_seconds = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Relationships ---
    course = relationship("Course", back_populates="lessons")

    progress_entries = relationship(
        "LessonProgress", back_populates="lesson", cascade="all, delete-orphan"
    )

    quizzes = relationship(
        "Quiz", back_populates="lesson", cascade="all, delete-orphan"
    )
