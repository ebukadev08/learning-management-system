"""
Pydantic schemas for Quiz, QuizQuestion, and QuizAttempt.

Note the two separate "question out" schemas:
 - QuestionForStudent: NO correct_answer field. This is what students
   get when they fetch a quiz to take it. If we sent correct_answer,
   they could read it straight out of the network response - same
   leak problem as video_url on the lesson list.
 - QuestionForInstructor: includes correct_answer, for the instructor
   managing their own quiz.
"""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.models.quiz_question import QuestionType


class QuizCreate(BaseModel):
    title: str
    lesson_id: Optional[int] = None  # null = final course-wide quiz
    passing_score: int = 70


class QuizOut(BaseModel):
    id: int
    course_id: int
    lesson_id: Optional[int]
    title: str
    passing_score: int
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None   # only for mcq
    correct_answer: str


class QuestionForStudent(BaseModel):
    id: int
    question_text: str
    question_type: QuestionType
    options: Optional[Any]
    # deliberately no correct_answer

    class Config:
        from_attributes = True


class QuestionForInstructor(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    question_type: QuestionType
    options: Optional[Any]
    correct_answer: str

    class Config:
        from_attributes = True


class QuizWithQuestions(BaseModel):
    id: int
    title: str
    passing_score: int
    questions: List[QuestionForStudent]

    class Config:
        from_attributes = True


class AnswerSubmission(BaseModel):
    question_id: int
    answer: str


class QuizSubmission(BaseModel):
    answers: List[AnswerSubmission]


class QuestionResult(BaseModel):
    question_id: int
    your_answer: str
    correct_answer: str
    is_correct: bool


class QuizResultOut(BaseModel):
    attempt_id: int
    quiz_id: int
    score: int
    passed: bool
    total_questions: int
    correct_count: int
    results: List[QuestionResult]