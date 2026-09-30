from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CertificateOut(BaseModel):
    id: int
    course_id: int
    certificate_url: Optional[str]
    issued_at: datetime

    class Config:
        from_attributes = True