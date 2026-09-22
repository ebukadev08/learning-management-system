"""
Importing every model here means: anywhere you do
    from app.models import Base
and then call Base.metadata.create_all(engine),
SQLAlchemy will know about ALL these tables, not just whichever one
you happened to import directly.

Without this, it's a classic gotcha: you import Base, call create_all(),
and half your tables silently don't get created because SQLAlchemy never
"saw" those model files.
"""

from app.core.database import Base

from app.models.user import User, UserRole
from app.models.course import Course, DifficultyLevel
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.models.lesson_progress import LessonProgress
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion, QuestionType
from app.models.quiz_attempt import QuizAttempt
from app.models.certificate import Certificate
from app.models.review import Review

__all__ = [
    "Base",
    "User", "UserRole",
    "Course", "DifficultyLevel",
    "Lesson",
    "Enrollment",
    "LessonProgress",
    "Quiz",
    "QuizQuestion", "QuestionType",
    "QuizAttempt",
    "Certificate",
    "Review",
]
