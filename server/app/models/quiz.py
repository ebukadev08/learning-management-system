"""
Quiz model.

A quiz can belong to a specific lesson (lesson_id set) OR be a final
course-wide quiz (lesson_id is null, only course_id set). This one table
covers both cases instead of needing "LessonQuiz" and "CourseQuiz" tables.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    # nullable: null = final course quiz, set = quiz tied to one lesson
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)

    title = Column(String(200), nullable=False)
    passing_score = Column(Integer, default=70)  # percentage required to pass

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Relationships ---
    course = relationship("Course", back_populates="quizzes")
    lesson = relationship("Lesson", back_populates="quizzes")

    questions = relationship(
        "QuizQuestion", back_populates="quiz", cascade="all, delete-orphan"
    )

    attempts = relationship(
        "QuizAttempt", back_populates="quiz", cascade="all, delete-orphan"
    )
