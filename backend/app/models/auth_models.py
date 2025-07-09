"""
Authentication models for request/response schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User-related models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    displayName: Optional[str] = None

class UserResponse(BaseModel):
    uid: str
    email: str
    displayName: Optional[str] = None
    isSubscribed: bool = False
    emailVerified: bool = False
    twoFactorEnabled: bool = False

class UserUpdate(BaseModel):
    displayName: Optional[str] = None

# Password reset models
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    newPassword: str

# Email verification models
class VerifyEmailRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    """Request model for resending verification email"""
    pass  # Uses current user from token

# Two-Factor Authentication models
class Setup2FAResponse(BaseModel):
    qr_code: str
    secret: str

class Verify2FARequest(BaseModel):
    code: str

class Enable2FARequest(BaseModel):
    code: str

class Disable2FARequest(BaseModel):
    code: str

class Login2FARequest(BaseModel):
    email: EmailStr
    password: str
    code: Optional[str] = None

# Session management models
class SessionResponse(BaseModel):
    sessionId: str
    expiresAt: Optional[datetime] = None
    isValid: bool

class SessionStatusResponse(BaseModel):
    sessionId: str
    expiresAt: Optional[datetime] = None
    isValid: bool
    timeRemaining: Optional[int] = None  # seconds

class ExtendSessionResponse(BaseModel):
    message: str
    expiresAt: datetime

# Generic response models
class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

# Internal data models (for Firestore)
class UserDocument(BaseModel):
    """Internal model for user document in Firestore"""
    uid: str
    email: str
    display_name: str
    subscription: bool = False
    stripe_id: str = ""
    email_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_expires: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    two_factor_secret_temp: Optional[str] = None
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None

class TokenData(BaseModel):
    """Model for token validation data"""
    uid: str
    email: str
    email_verified: bool
    firebase_claims: dict