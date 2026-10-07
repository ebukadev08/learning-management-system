"""
FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload

Then visit http://127.0.0.1:8000/docs for the auto-generated Swagger UI -
this is the "free interactive API docs" FastAPI gives you.
"""

from fastapi import FastAPI
from app.core.database import engine
from fastapi.middleware.cors import CORSMiddleware
from app.models import Base
from app.routes import auth
from app.routes import courses
from app.routes import lessons
from app.routes import enrollments
from app.routes import progress
from app.routes import quizzes
from app.routes import certificates
from app.routes import reviews
from app.routes import instructor


# Creates all tables in MySQL if they don't already exist.
# Safe to run every startup - it won't touch tables that already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Online Learning Platform API",
    description="Backend API for an LMS - courses, lessons, quizzes, progress tracking, certificates.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(lessons.router, prefix="/api", tags=["Lessons"])
app.include_router(enrollments.router, prefix="/api", tags=["Enrollments"])
app.include_router(progress.router, prefix="/api", tags=["Progress"])
app.include_router(quizzes.router, prefix="/api", tags=["Quizzes"])
app.include_router(certificates.router, prefix="/api", tags=["Certificates"])
app.include_router(reviews.router, prefix="/api", tags=["Reviews"])
app.include_router(instructor.router, prefix="/api", tags=["Instructor Dashboard"])


@app.get("/")
def root():
    return {"message": "Online Learning Platform API is running"}


# Routers will be plugged in here as we build each phase, e.g.:
# from app.routes import auth
# app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
