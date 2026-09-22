"""
QuizAttempt model.

Every time a student submits a quiz, we insert a new row here rather than
overwriting - this gives you attempt history for free (e.g. "show best
score", "allow 3 tries"), which you'd lose if you only stored one result
per student per quiz.
"""

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)

    score = Column(Integer, nullable=False)  # percentage, 0-100
    passed = Column(Boolean, default=False)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Relationships ---
    student = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")
