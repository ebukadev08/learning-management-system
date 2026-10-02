"""
Instructor dashboard routes.

Aggregates data across an instructor's own courses: enrollment counts,
ratings, completion rates, and per-course student lists. Every query
here is scoped to current_user.id as the instructor - an instructor
can never see another instructor's numbers.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.review import Review
from app.models.lesson import Lesson
from app.models.user import User
from app.schemas.instructor import InstructorDashboardOut, CourseSummary, EnrolledStudentOut
from app.utils.dependencies import require_instructor

router = APIRouter()


@router.get("/instructor/dashboard", response_model=InstructorDashboardOut)
def get_instructor_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor),
):
    courses = db.query(Course).filter(Course.instructor_id == current_user.id).all()

    course_summaries = []
    all_student_ids = set()

    for course in courses:
        enrollments = db.query(Enrollment).filter(Enrollment.course_id == course.id).all()
        enrolled_count = len(enrollments)

        for e in enrollments:
            all_student_ids.add(e.user_id)

        completed_count = sum(1 for e in enrollments if e.completed)
        completion_rate = (
            round((completed_count / enrolled_count) * 100, 1) if enrolled_count > 0 else 0.0
        )

        rating_result = (
            db.query(
                func.avg(Review.rating).label("avg_rating"),
                func.count(Review.id).label("review_count"),
            )
            .filter(Review.course_id == course.id)
            .first()
        )
        average_rating = round(float(rating_result.avg_rating), 1) if rating_result.avg_rating else 0.0

        course_summaries.append(
            CourseSummary(
                course_id=course.id,
                title=course.title,
                enrolled_count=enrolled_count,
                average_rating=average_rating,
                total_reviews=rating_result.review_count,
                completion_rate=completion_rate,
            )
        )

    return InstructorDashboardOut(
        total_courses=len(courses),
        total_students=len(all_student_ids),
        courses=course_summaries,
    )


@router.get(
    "/instructor/courses/{course_id}/students",
    response_model=List[EnrolledStudentOut],
)
def get_enrolled_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    if course.instructor_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view students for your own courses.",
        )

    total_lessons = db.query(Lesson).filter(Lesson.course_id == course_id).count()

    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()

    results = []
    for enrollment in enrollments:
        student = enrollment.student  # via relationship

        completed_lessons = sum(1 for p in enrollment.lesson_progress if p.completed)
        progress_percent = (
            round((completed_lessons / total_lessons) * 100, 1) if total_lessons > 0 else 0.0
        )

        results.append(
            EnrolledStudentOut(
                user_id=student.id,
                name=student.name,
                email=student.email,
                enrolled_at=enrollment.enrolled_at.isoformat(),
                progress_percent=progress_percent,
                completed=enrollment.completed,
            )
        )

    return results