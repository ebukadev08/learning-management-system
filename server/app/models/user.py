"""
User model.

One table for everyone (students, instructors, admins) using a `role`
column instead of separate tables. This keeps auth logic simple - one
login endpoint, one users table - and lets a single account act as an
instructor on their own courses while being a student in others.
"""

import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    student = "student"
    instructor = "instructor"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.student, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Relationships ---
    # Courses this user teaches (only meaningful if role == instructor)
    courses_taught = relationship(
        "Course", back_populates="instructor", cascade="all, delete-orphan"
    )

    # Courses this user is enrolled in, via the enrollments join table
    enrollments = relationship(
        "Enrollment", back_populates="student", cascade="all, delete-orphan"
    )

    quiz_attempts = relationship(
        "QuizAttempt", back_populates="student", cascade="all, delete-orphan"
    )

    certificates = relationship(
        "Certificate", back_populates="student", cascade="all, delete-orphan"
    )

    reviews = relationship(
        "Review", back_populates="student", cascade="all, delete-orphan"
    )
