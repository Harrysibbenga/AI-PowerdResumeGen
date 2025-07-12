from pydantic import EmailStr
from .base import BaseModel

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ChangePasswordResponse(BaseModel):
    message: str
