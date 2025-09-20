from pydantic import validator, EmailStr
from typing import Optional, List
from .base import BaseModel

class Language(BaseModel):
    """Language with proficiency level"""
    language: str
    proficiency: str
    
class Skill(BaseModel):
    """Skills"""
    skill: str

class Experience(BaseModel):
    """Work Experience """
    title: str
    company: str
    location: Optional[str] = None
    start_date: str  # Format: "YYYY-MM"
    end_date: Optional[str] = None  # Format: "YYYY-MM" or None if current
    current: bool = False
    description: str
    highlights: List[str] = []

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v is None and not values.get('current', False):
            return v
        return v

class Education(BaseModel):
    """Education"""
    degree: str
    school: str
    location: Optional[str] = None
    graduation_date: str  # Format: "YYYY-MM"
    description: Optional[str] = None
    gpa: Optional[str] = None

class Project(BaseModel):
    """Project"""
    title: str
    description: str
    technologies: List[str] = []
    url: Optional[str] = None
    start_date: Optional[str] = None  # Format: "YYYY-MM"
    end_date: Optional[str] = None    # Format: "YYYY-MM"
    highlights: List[str] = []
    
class Certification(BaseModel):
    """Certificatons"""
    name: str
    issuer: str 
    date: str  # Format: "YYYY-MM"
    expiryDate: Optional[str] = None  # Format: "YYYY-MM" or None if current
    credentialId: Optional[str] = None

class UserProfile(BaseModel):
    """UserProfile"""
    # Basic personal info
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    
    # Professional details
    skills: List[Skill] = []
    work_experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    skills: List[str] = []
    certifications: List[Certification] = []
    languages: List[Language] = []

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v

    @validator('languages', pre=True)
    def validate_languages(cls, v):
        """Handle both old string format and new object format"""
        if not v:
            return []

        result = []
        for lang in v:
            if isinstance(lang, str):
                import re
                match = re.match(r'^(.+?)\s*\((.+?)\)$', lang)
                if match:
                    result.append(Language(language=match.group(1).strip(), proficiency=match.group(2).strip()))
                else:
                    result.append(Language(language=lang.strip(), proficiency='Intermediate'))
            elif isinstance(lang, dict):
                result.append(Language(**lang))
            else:
                result.append(lang)
        return result
