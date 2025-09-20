from .base import BaseModel
from datetime import datetime
from typing import Optional

class SessionResponse(BaseModel):
    session_id: str
    expires_at: Optional[datetime] = None
    is_valid: bool

class SessionStatusResponse(BaseModel):
    session_id: str
    expires_at: Optional[datetime] = None
    is_valid: bool
    time_remaining: Optional[int] = None

class ExtendSessionResponse(BaseModel):
    message: str
    expires_at: datetime
