from .base import BaseModel
from typing import Optional
from .user import UserResponse

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse
    requires_2fa: Optional[bool] = False

class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
