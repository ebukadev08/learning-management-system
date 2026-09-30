"""
Review routes.

Enrollment is required to post a review (you must have taken the course).
Ownership is required to edit/delete (only your own review).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut, CourseRatingSummary
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/courses/{course_id}/reviews",
    response_model=ReviewOut,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    course_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id, Enrollment.course_id == course_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be enrolled in this course to review it.",
        )

    existing = (
        db.query(Review)
        .filter(Review.user_id == current_user.id, Review.course_id == course_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="You've already reviewed this course. Use PUT to edit it instead.",
        )

    new_review = Review(
        user_id=current_user.id,
        course_id=course_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )
    db.add(new_review)
    try:
        db.commit()
        db.refresh(new_review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="You've already reviewed this course.")

    return new_review


@router.get("/courses/{course_id}/reviews", response_model=List[ReviewOut])
def list_course_reviews(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    return (
        db.query(Review)
        .filter(Review.course_id == course_id)
        .order_by(Review.created_at.desc())
        .all()
    )


@router.get("/courses/{course_id}/rating", response_model=CourseRatingSummary)
def get_course_rating(course_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(
            func.avg(Review.rating).label("average_rating"),
            func.count(Review.id).label("total_reviews"),
        )
        .filter(Review.course_id == course_id)
        .first()
    )

    average = round(float(result.average_rating), 1) if result.average_rating else 0.0

    return CourseRatingSummary(
        course_id=course_id,
        average_rating=average,
        total_reviews=result.total_reviews,
    )


@router.put("/reviews/{review_id}", response_model=ReviewOut)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own review.",
        )

    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)
    return review


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own review.",
        )

    db.delete(review)
    db.commit()
    return None