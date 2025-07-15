from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from .base import ResumeTone, ResumeLength, ResumeTemplate
from .profile import UserProfile

class ResumeRequest(BaseModel):
    # Resume metadata
    title: str
    target_job_title: str
    target_job_role: Optional[str] = None
    target_company: Optional[str] = None
    
    # User profile data
    profile: UserProfile
    
    # AI generation settings
    tone: ResumeTone = ResumeTone.PROFESSIONAL
    length: ResumeLength = ResumeLength.STANDARD
    template_id: ResumeTemplate = ResumeTemplate.MODERN
    
    # Additional options
    include_projects: bool = True
    include_certifications: bool = True
    include_languages: bool = False
    focus_keywords: Optional[str] = None
    
    # Custom sections
    custom_sections: Optional[Dict[str, Any]] = None

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Resume title cannot be empty')
        return v.strip()

    @validator('target_job_title')
    def validate_target_job_title(cls, v):
        if not v.strip():
            raise ValueError('Target job title cannot be empty')
        return v.strip()

class ResumeUpdateRequest(BaseModel):
    title: Optional[str] = None
    target_job_title: Optional[str] = None
    target_job_role: Optional[str] = None
    target_company: Optional[str] = None
    tone: Optional[ResumeTone] = None
    length: Optional[ResumeLength] = None
    template_id: Optional[ResumeTemplate] = None
    focus_keywords: Optional[str] = None
    profile: Optional[UserProfile] = None