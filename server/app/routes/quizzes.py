"""
Quiz routes.

Instructor side: create quiz, add questions, view questions (with answers)
Student side: fetch quiz to take (answers hidden), submit attempt, view own attempts
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.schemas.quiz import (
    QuizCreate, QuizOut, QuestionCreate, QuestionForInstructor,
    QuizWithQuestions, QuizSubmission, QuizResultOut, QuestionResult,
)
from app.utils.dependencies import get_current_user, require_instructor
from app.utils.grading import is_answer_correct, calculate_score

router = APIRouter()

def _get_owned_course(course_id: int, current_user: User, db: Session) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    if course.instructor_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage quizzes on your own courses.",
        )
    return course

def _require_enrollment(course_id: int, current_user: User, db: Session) -> Enrollment:
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id, Enrollment.course_id == course_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be enrolled in this course to access its quizzes.",
        )
    return enrollment


@router.post(
    "/courses/{course_id}/quizzes",
    response_model=QuizOut,
    status_code=status.HTTP_201_CREATED,
)
def create_quiz(
    course_id: int,
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor),
):
    _get_owned_course(course_id, current_user, db)

    new_quiz = Quiz(**quiz_data.model_dump(), course_id=course_id)
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    return new_quiz

@router.post("/quizzes/{quiz_id}/questions", response_model=QuestionForInstructor, status_code=status.HTTP_201_CREATED)
def add_question(
    quiz_id: int,
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    _get_owned_course(quiz.course_id, current_user, db)

    if question_data.question_type.value == "mcq":
        if not question_data.options or len(question_data.options) < 2:
            raise HTTPException(
                status_code=400,
                detail="Multiple choice questions need at least 2 option"
            )
        if question_data.correct_answer not in question_data.options:
            raise HTTPException(
                status_code=400,
                detail="correct_answer must be one the provided options"
            )

    new_question = QuizQuestion(**question_data.model_dump(), quiz_id=quiz_id)
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@router.get(
    "/quizzes/{quiz_id}/questions/manage",
    response_model=List[QuestionForInstructor],
)
def list_questions_for_instructor(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    _get_owned_course(quiz.course_id, current_user, db)

    return db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()

# ---------- Student endpoints ----------

@router.get("/courses/{course_id}/quizzes", response_model=List[QuizOut])
def list_course_quizzes(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_enrollment(course_id, current_user, db)
    return db.query(Quiz).filter(Quiz.course_id == course_id).all()

@router.get("/quizzes/{quiz_id}", response_model=QuizWithQuestions)
def get_quiz_to_take(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    _require_enrollment(quiz.course_id, current_user, db)
    return quiz

@router.post("/quizzes/{quiz_id}/submit", response_model=QuizResultOut)
def submit_quiz(
    quiz_id: int,
    submission: QuizSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    _require_enrollment(quiz.course_id, current_user, db)

    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
    if not questions:
        raise HTTPException(status_code=400, detail="This quiz has no questions yet.")

    submitted_map = {a.question_id: a.answer for a in submission.answers}
    results = []
    correct_count = 0

    for question in questions:
        student_answer = submitted_map.get(question.id, "")
        correct = is_answer_correct(question, student_answer)
        if correct:
            correct_count += 1

        results.append(
            QuestionResult(
                question_id=question.id,
                your_answer=student_answer,
                correct_answer=question.correct_answer,
                is_correct=correct,
            )
        )

    score = calculate_score(correct_count, len(questions))
    passed = score >= quiz.passing_score

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        passed=passed
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return QuizResultOut(
        attempt_id=attempt.id,
        quiz_id=quiz_id,
        score=score,
        passed=passed,
        total_questions=len(questions),
        correct_count=correct_count,
        results=results,
    )

@router.get("/quizzes/{quiz_id}/my-attempts")
def get_my_attempts(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
): 
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == current_user.id, QuizAttempt.quiz_id == quiz_id)
        .order_by(QuizAttempt.attempted_at.desc())
        .all()
    )
    return{
        "quiz_id": quiz_id,
        "attempt_count": len(attempts),
        "best_score": max((a.score for a in attempts), default=0),
        "attempts": [
            {"id": a.id, "score": a.score, "passed": a.passed, "attempted_at": a.attempted_at } for a in attempts
        ]
    }
