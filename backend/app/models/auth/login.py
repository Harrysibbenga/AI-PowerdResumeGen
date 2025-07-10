from pydantic import EmailStr
from .base import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class LoginWith2FARequest(LoginRequest):
    two_factor_code: Optional[str] = None

class Login2FARequest(LoginRequest):
    code: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
