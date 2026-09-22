"""
Review model.

One review per student per course, enforced by UniqueConstraint - matches
the requirement that users can edit/delete their OWN review rather than
post multiple. `updated_at` lets you show "edited" on the frontend later.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_review"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_rating_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # --- Relationships ---
    student = relationship("User", back_populates="reviews")
    course = relationship("Course", back_populates="reviews")
