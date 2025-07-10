from pydantic import EmailStr
from .base import BaseModel
from typing import Optional, List
from datetime import datetime

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

class UserDocument(BaseModel):
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
    refresh_tokens: Optional[List[str]] = []
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    failed_login_attempts: Optional[int] = 0
    account_locked_until: Optional[datetime] = None
