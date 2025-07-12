from pydantic import EmailStr
from .base import BaseModel

class PasswordValidationRequest(BaseModel):
    password: str

class PasswordValidationResponse(BaseModel):
    score: int
    strength: str
    is_strong: bool
    suggestions: list[str]