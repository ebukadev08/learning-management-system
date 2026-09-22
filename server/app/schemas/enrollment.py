from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EnrollmentOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
    completed: bool
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True