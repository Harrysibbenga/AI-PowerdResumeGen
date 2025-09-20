from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class Language(BaseModel):
    """Language with proficiency level"""
    language: str
    proficiency: str

class Experience(BaseModel):
    """Work Experience - updated to match frontend"""
    title: str
    company: str
    location: Optional[str] = None
    startDate: str  # Format: "YYYY-MM"
    endDate: Optional[str] = None  # Format: "YYYY-MM" or None if current
    current: bool = False
    description: str
    highlights: List[str] = []  # Added highlights field

    @validator('endDate')
    def validate_end_date(cls, v, values):
        if v is None and not values.get('current', False):
            # Allow None endDate without requiring current=True
            return v
        return v

class Education(BaseModel):
    """Education - updated to match frontend"""
    degree: str
    school: str  # Changed from 'institution' to 'school'
    location: Optional[str] = None
    graduationDate: str  # Changed from startYear/endYear to graduationDate (YYYY-MM format)
    description: Optional[str] = None
    gpa: Optional[str] = None  # Changed from float to string to handle "3.8" format

class Project(BaseModel):
    """Project - updated to match new frontend structure"""
    title: str
    description: str
    technologies: List[str] = []
    url: Optional[str] = None
    startDate: Optional[str] = None  # Format: "YYYY-MM"
    endDate: Optional[str] = None    # Format: "YYYY-MM"
    highlights: List[str] = []

class UserProfile(BaseModel):
    """Updated UserProfile to match frontend form data"""
    # Basic personal info
    fullName: str  # Changed from 'name' to 'fullName'
    email: EmailStr
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None
    
    # Professional details
    workExperience: List[Experience] = []  # Changed from 'experience' to 'workExperience'
    education: List[Education] = []
    projects: List[Project] = []
    skills: List[str] = []
    certifications: List[str] = []
    languages: List[Language] = []  # Updated to use Language model instead of strings
    
    # Industry and role information
    industry: str
    
    # Professional summary
    summary: Optional[str] = None  # Changed from 'professional_summary' to 'summary'

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
                # Try to parse old format: "Spanish (Fluent)"
                import re
                match = re.match(r'^(.+?)\s*\((.+?)\)$', lang)
                if match:
                    result.append(Language(language=match.group(1).strip(), proficiency=match.group(2).strip()))
                else:
                    # Fallback for languages without proficiency
                    result.append(Language(language=lang.strip(), proficiency='Intermediate'))
            elif isinstance(lang, dict):
                result.append(Language(**lang))
            else:
                result.append(lang)  # Already a Language object
        return result
