"""
Course model.

Each course belongs to exactly one instructor (a User with role=instructor).
"""

import enum
from sqlalchemy import (
    Column, Integer, String, Text, Float, Enum, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class DifficultyLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.beginner)
    thumbnail_url = Column(String(500), nullable=True)
    price = Column(Float, default=0.0)  # 0.0 = free course

    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # --- Relationships ---
    instructor = relationship("User", back_populates="courses_taught")

    lessons = relationship(
        "Lesson", back_populates="course",
        cascade="all, delete-orphan", order_by="Lesson.order_index"
    )

    enrollments = relationship(
        "Enrollment", back_populates="course", cascade="all, delete-orphan"
    )

    quizzes = relationship(
        "Quiz", back_populates="course", cascade="all, delete-orphan"
    )

    reviews = relationship(
        "Review", back_populates="course", cascade="all, delete-orphan"
    )

    certificates = relationship(
        "Certificate", back_populates="course", cascade="all, delete-orphan"
    )
