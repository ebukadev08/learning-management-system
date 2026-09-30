"""
Certificate routes.

Eligibility for a certificate:
 1. enrollment.completed == True (every lesson watched - set automatically
    by the progress phase)
 2. every quiz in the course has at least one PASSED attempt by this student

We check both, generate the PDF only if eligible, and store the file path.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.certificate import Certificate
from app.models.user import User
from app.schemas.certificate import CertificateOut
from app.utils.dependencies import get_current_user
from app.utils.certificate_generator import generate_certificate_pdf

router = APIRouter()

def _check_eligibility(user: User, course_id: int, db: Session) -> Enrollment:
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id, Enrollment.course_id == course_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=404, detail="You are not enrolled in this course.")

    if not enrollment.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must complete all lessons before receiving a certificate.",
        )

    course_quizzes = db.query(Quiz).filter(Quiz.course_id == course_id).all()
    for quiz in course_quizzes:
        passed_attempt = (
            db.query(QuizAttempt)
            .filter(
                QuizAttempt.user_id == user.id,
                QuizAttempt.quiz_id == quiz.id,
                QuizAttempt.passed == True,  # noqa: E712
            )
            .first()
        )
        if not passed_attempt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You must pass the quiz '{quiz.title}' before receiving a certificate.",
            )

    return enrollment

@router.post(
    "/courses/{course_id}/certificate",
    response_model=CertificateOut,
    status_code=status.HTTP_201_CREATED,
)
def issue_certificate(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    # Already issued? Return the existing one instead of duplicating.
    existing = (
        db.query(Certificate)
        .filter(Certificate.user_id == current_user.id, Certificate.course_id == course_id)
        .first()
    )
    if existing:
        return existing

    _check_eligibility(current_user, course_id, db)

    new_certificate = Certificate(user_id=current_user.id, course_id=course_id)
    db.add(new_certificate)
    try:
        db.commit()
        db.refresh(new_certificate)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Certificate already exists.")

    filepath = generate_certificate_pdf(
        student_name=current_user.name,
        course_title=course.title,
        certificate_id=new_certificate.id,
    )
    new_certificate.certificate_url = filepath
    db.commit()
    db.refresh(new_certificate)

    return new_certificate

@router.get("/certificates/me", response_model=list[CertificateOut])
def list_my_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Certificate).filter(Certificate.user_id == current_user.id).all()

@router.get("/certificates/{certificate_id}/download")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found.")

    if certificate.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only download your own certificates.",
        )

    if not certificate.certificate_url or not os.path.exists(certificate.certificate_url):
        raise HTTPException(status_code=404, detail="Certificate file not found.")

    return FileResponse(
        path=certificate.certificate_url,
        media_type="application/pdf",
        filename=f"certificate_{certificate_id}.pdf",
    )