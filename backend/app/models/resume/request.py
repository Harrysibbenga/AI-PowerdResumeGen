from pydantic import validator
from typing import Optional, Dict, Any
from .base import BaseModel, ResumeTone, ResumeLength, ResumeTemplate
from .profile import UserProfile

class ResumeRequest(BaseModel):
    # Resume metadata
    title: str
    target_job_title: str  
    target_job_role: Optional[str] = None  
    target_company: Optional[str] = None  
    industry: str
    
    # User profile data
    profile_data: UserProfile
    
    # AI generation settings
    ai_tone: ResumeTone = ResumeTone.PROFESSIONAL  
    ai_length: ResumeLength = ResumeLength.STANDARD  
    template_id: ResumeTemplate = ResumeTemplate.MODERN
    
    # Section inclusion flags
    include_projects: bool = True  
    include_certifications: bool = True  
    include_languages: bool = True  
    
    # Additional options
    focus_keywords: Optional[str] = None  
    use_ai: bool = True 
    
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
    # Resume metadata
    title: Optional[str] = None
    target_job_title: Optional[str] = None
    target_job_role: Optional[str] = None
    target_company: Optional[str] = None
    industry: Optional[str] = None
    
    # User profile data
    profile_data: Optional[UserProfile]
    
    # AI generation settings
    ai_tone: Optional[ResumeTone] = None
    ai_length: Optional[ResumeLength] = None
    template_id: Optional[ResumeTemplate] = None
    
    # Section inclusion flags (matching what frontend sends)
    include_projects: Optional[bool] = None
    include_certifications: Optional[bool] = None
    include_languages: Optional[bool] = None
    
    # Additional options
    focus_keywords: Optional[str] = None
    use_ai: Optional[bool] = None
    
    # Custom sections
    custom_sections: Optional[Dict[str, Any]] = None