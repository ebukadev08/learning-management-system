"""
Lesson routes.

Lessons are nested under a course for creation/listing
(/api/courses/{course_id}/lessons), but have their own top-level routes
for get/update/delete by lesson id, since a lesson is uniquely identified
without needing its course in the URL at that point.

Ownership is checked through the lesson's course - only the instructor
who owns course.instructor_id can add/edit/delete its lessons.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.user import User
from app.models.enrollment import Enrollment
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonOut, LessonPreviewOut
from app.utils.dependencies import require_instructor
from app.utils.dependencies import get_current_user

router = APIRouter()


def _get_owned_course(course_id: int, current_user: User, db: Session) -> Course:
    """Shared helper: fetch a course and confirm current_user owns it."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    if course.instructor_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage lessons on your own courses.",
        )
    return course


@router.post(
    "/courses/{course_id}/lessons",
    response_model=LessonOut,
    status_code=status.HTTP_201_CREATED,
)
def create_lesson(
    course_id: int,
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor),
):
    _get_owned_course(course_id, current_user, db)

    new_lesson = Lesson(**lesson_data.model_dump(), course_id=course_id)
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson


@router.get("/courses/{course_id}/lessons", response_model=List[LessonPreviewOut])
def list_lessons(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    return (
        db.query(Lesson)
        .filter(Lesson.course_id == course_id)
        .order_by(Lesson.order_index)
        .all()
    )


@router.get("/lessons/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")


    is_owner = course.instructor_id == current_user.id

    is_enrolled = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id, Enrollment.course_id == course.id)
        .first()
        is not None
    )

    if not (is_owner or is_enrolled or current_user.role.value == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be enrolled in this course to view this lesson."
        )

    return lesson


@router.put("/lessons/{lesson_id}", response_model=LessonOut)
def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    _get_owned_course(lesson.course_id, current_user, db)

    update_data = lesson_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lesson, field, value)

    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    _get_owned_course(lesson.course_id, current_user, db)

    db.delete(lesson)
    db.commit()
    return None