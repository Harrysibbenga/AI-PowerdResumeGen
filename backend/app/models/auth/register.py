# app/models/register.py
from pydantic import EmailStr, validator
from .base import BaseModel
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    terms_agreed: bool = True
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('display_name')
    def validate_display_name(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Display name is required')
        if len(v.strip()) > 100:
            raise ValueError('Display name must be less than 100 characters')
        return v.strip()
    
    @validator('terms_agreed')
    def validate_terms(cls, v):
        if not v:
            raise ValueError('You must agree to the terms and conditions')
        return v

class RegisterRequestToken(BaseModel):
    id_token: str
    display_name: str
    
    @validator('display_name')
    def validate_display_name(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Display name is required')
        if len(v.strip()) > 100:
            raise ValueError('Display name must be less than 100 characters')
        return v.strip()

class RegisterResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: 'UserResponse'
    message: str = "Account created successfully"

class EmailVerificationRequest(BaseModel):
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    token: str
    email: EmailStr

class ResendVerificationRequest(BaseModel):
    id_token: str

# Import to avoid circular imports
from app.models.auth import UserResponse
RegisterResponse.model_rebuild()