"""
Certificate model.

Issued once a student finishes every lesson AND passes every quiz in a
course. certificate_url points to the generated PDF (we'll build the
pdfkit generation logic when we get to this phase).

UniqueConstraint stops duplicate certificates being issued for the same
student+course.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Certificate(Base):
    __tablename__ = "certificates"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_certificate"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    certificate_url = Column(String(500), nullable=True)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Relationships ---
    student = relationship("User", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")
