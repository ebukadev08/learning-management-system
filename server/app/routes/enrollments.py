from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.enrollment import EnrollmentOut
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.post(
    "/courses/{course_id}/enroll", 
    response_model=EnrollmentOut, 
    status_code=status.HTTP_201_CREATED
)

def enroll_in_course(
    course_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    if course.instructor_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="you can not enroll your own course")

    existing= (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id, Enrollment.course_id == course_id).first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course.")

    new_enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    db.add(new_enrollment)
    try:
        db.commit()
        db.refresh(new_enrollment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already enrolled in this course.")

    return new_enrollment

@router.get("/enrollment/me", response_model=List[EnrollmentOut])
def list_my_enrollment(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
):
    return db.query(Enrollment).filter(Enrollment.user_id == current_user.id).all()

@router.get("/courses/{course_id}/enrollment", response_model=EnrollmentOut)
def get_my_enrollment_for_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id, Enrollment.course_id == course_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not enrolled in this course.")
    return enrollment

@router.delete("/courses/{course_id}/enroll", status_code=status.HTTP_204_NO_CONTENT)
def uneroll_from_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id, Enrollment.course_id == course_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=404, detail="You are not enrolled in this course.")

    db.delete(enrollment)
    db.commit()
    return None

