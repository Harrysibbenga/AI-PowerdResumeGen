from .base import BaseModel

class Setup2FAResponse(BaseModel):
    qr_code: str
    secret: str

class Verify2FARequest(BaseModel):
    code: str

class Enable2FARequest(BaseModel):
    code: str

class Disable2FARequest(BaseModel):
    code: str
