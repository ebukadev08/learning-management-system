"""
FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload

Then visit http://127.0.0.1:8000/docs for the auto-generated Swagger UI -
this is the "free interactive API docs" FastAPI gives you.
"""

from fastapi import FastAPI
from app.core.database import engine
from app.models import Base
from app.routes import auth
from app.routes import courses
from app.routes import lessons
from app.routes import enrollments
from app.routes import progress
from app.routes import quizzes
from app.routes import certificates


# Creates all tables in MySQL if they don't already exist.
# Safe to run every startup - it won't touch tables that already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Online Learning Platform API",
    description="Backend API for an LMS - courses, lessons, quizzes, progress tracking, certificates.",
    version="0.1.0",
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(lessons.router, prefix="/api", tags=["Lessons"])
app.include_router(enrollments.router, prefix="/api", tags=["Enrollments"])
app.include_router(progress.router, prefix="/api", tags=["Progress"])
app.include_router(quizzes.router, prefix="/api", tags=["Quizzes"])
app.include_router(certificates.router, prefix="/api", tags=["Certificates"])


@app.get("/")
def root():
    return {"message": "Online Learning Platform API is running"}


# Routers will be plugged in here as we build each phase, e.g.:
# from app.routes import auth
# app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
