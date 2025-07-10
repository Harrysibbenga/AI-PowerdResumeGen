from .base import BaseModel
from typing import Dict

class TokenData(BaseModel):
    uid: str
    email: str
    email_verified: bool
    firebase_claims: Dict
