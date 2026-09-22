from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.models.lesson_progress import LessonProgress
from app.models.user import User
from app.schemas.progress import ProgressUpdate, LessonProgressOut, CourseProgressOut
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.post("/lessons/{lesson_id}/progress", response_model=LessonProgressOut)
def update_lesson_progress(
    lesson_id: int,
    progress_data: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == lesson.course_id,
        )
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be enrolled in this course to track progress.",
        )

    progress = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.enrollment_id == enrollment.id,
            LessonProgress.lesson_id == lesson_id,
        )
        .first()
    )

    if not progress:
        progress = LessonProgress(enrollment_id=enrollment.id, lesson_id=lesson_id)
        db.add(progress)

    progress.watched_seconds = progress_data.watch_seconds

    if progress_data.completed is not None:
        is_now_completed = progress_data.completed
    else:
        is_now_completed = (
            lesson.duration_seconds > 0
            and progress_data.watch_seconds >= lesson.duration_seconds
        )

    if is_now_completed and not progress.completed:
        progress.completed = True
        progress.completed_at = datetime.now(timezone.utc)
    elif not is_now_completed:
        progress.completed = False
        progress.completed_at = None

    db.commit()
    db.refresh(progress)

    _check_and_update_course_completion(enrollment, db)

    return progress

@router.get("/courses/{course_id}/progress", response_model=CourseProgressOut)
def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id, Enrollment.course_id == course_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=404, detail="You are not enrolled in this course.")

    total_lessons = db.query(Lesson).filter(Lesson.course_id == course_id).count()
    completed_lessons = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.enrollment_id == enrollment.id,
            LessonProgress.completed == True,  # noqa: E712
        )
        .count()
    )

    percent = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0

    return CourseProgressOut(
        course_id=course_id,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        percent_complete=round(percent, 1),
        course_completed=enrollment.completed,
    )


def _check_and_update_course_completion(enrollment: Enrollment, db: Session):
    """
    Called after every progress update. If every lesson in the course is
    now marked complete, flip the enrollment itself to completed=True.
    This is what will later trigger certificate eligibility.
    """
    total_lessons = (
        db.query(Lesson).filter(Lesson.course_id == enrollment.course_id).count()
    )
    completed_lessons = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.enrollment_id == enrollment.id,
            LessonProgress.completed == True,
        )
        .count()
    )

    all_done = total_lessons > 0 and completed_lessons == total_lessons

    if all_done and not enrollment.completed:
        enrollment.completed = True
        enrollment.completed_at = datetime.now(timezone.utc)
        db.commit()
    elif not all_done and enrollment.completed:
        # Edge case: if a student's progress got reset on a lesson,
        # un-complete the course too, so it stays accurate.
        enrollment.completed = False
        enrollment.completed_at = None
        db.commit()
