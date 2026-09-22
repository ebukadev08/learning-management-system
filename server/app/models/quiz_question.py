"""
QuizQuestion model.

Supports 3 question types via `question_type`:
 - mcq: options is a JSON list e.g. ["Paris", "London", "Rome"], correct_answer
        is the matching string e.g. "Paris"
 - true_false: options is null, correct_answer is "true" or "false"
 - fill_blank: options is null, correct_answer is the expected text
               (auto-grading does a case-insensitive match)

Using a JSON column for `options` avoids needing a separate
"question_options" table for something this simple.
"""

import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class QuestionType(str, enum.Enum):
    mcq = "mcq"
    true_false = "true_false"
    fill_blank = "fill_blank"


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)

    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    options = Column(JSON, nullable=True)  # only used for mcq
    correct_answer = Column(String(255), nullable=False)

    # --- Relationships ---
    quiz = relationship("Quiz", back_populates="questions")
