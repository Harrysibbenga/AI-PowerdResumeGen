from .base import BaseModel

class VerifyEmailRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    """Empty request body – uses token from current user"""
    pass
