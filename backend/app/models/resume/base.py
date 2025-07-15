from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ExportFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"

class ExportStatus(str, Enum):
    FREE = "free"
    PAID = "paid"
    SUBSCRIBED = "subscribed"

class ResumeTone(str, Enum):
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    FORMAL = "formal"
    CASUAL = "casual"

class ResumeLength(str, Enum):
    SHORT = "short"
    STANDARD = "standard"
    DETAILED = "detailed"

class ResumeTemplate(str, Enum):
    MODERN = "modern"
    CLASSIC = "classic"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    EXECUTIVE = "executive"