from .base import BaseModel
from datetime import datetime
from typing import Optional

class SessionResponse(BaseModel):
    sessionId: str
    expiresAt: Optional[datetime] = None
    isValid: bool

class SessionStatusResponse(BaseModel):
    sessionId: str
    expiresAt: Optional[datetime] = None
    isValid: bool
    timeRemaining: Optional[int] = None

class ExtendSessionResponse(BaseModel):
    message: str
    expiresAt: datetime
