from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from .base import ResumeTone, ResumeLength, ResumeTemplate
from .profile import UserProfile

class ResumeRequest(BaseModel):
    # Resume metadata
    title: str
    targetJobTitle: str  
    targetJobRole: Optional[str] = None  
    targetCompany: Optional[str] = None  
    
    # User profile data
    profile: UserProfile
    
    # AI generation settings
    aiTone: ResumeTone = ResumeTone.PROFESSIONAL  
    aiLength: ResumeLength = ResumeLength.STANDARD  
    template_id: ResumeTemplate = ResumeTemplate.MODERN
    
    # Section inclusion flags
    includeProjects: bool = True  
    includeCertifications: bool = True  
    includeLanguages: bool = False  
    
    # Additional options
    focusKeywords: Optional[str] = None  
    useAI: bool = True 
    
    # Custom sections
    custom_sections: Optional[Dict[str, Any]] = None

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Resume title cannot be empty')
        return v.strip()

    @validator('targetJobTitle')
    def validate_target_job_title(cls, v):
        if not v.strip():
            raise ValueError('Target job title cannot be empty')
        return v.strip()

class ResumeUpdateRequest(BaseModel):
    title: Optional[str] = None
    targetJobTitle: Optional[str] = None
    targetJobRole: Optional[str] = None
    targetCompany: Optional[str] = None
    aiTone: Optional[ResumeTone] = None
    aiLength: Optional[ResumeLength] = None
    template_id: Optional[ResumeTemplate] = None
    focusKeywords: Optional[str] = None
    profile: Optional[UserProfile] = None