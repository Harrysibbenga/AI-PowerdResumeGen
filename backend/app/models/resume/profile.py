from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    startDate: str
    endDate: Optional[str] = None
    current: bool = False
    description: str

    @validator('endDate')
    def validate_end_date(cls, v, values):
        if v is None and not values.get('current', False):
            raise ValueError('End date is required unless position is current')
        return v

class Education(BaseModel):
    degree: str
    institution: str
    location: Optional[str] = None
    startYear: int
    endYear: Optional[int] = None
    description: Optional[str] = None
    gpa: Optional[float] = None

    @validator('endYear')
    def validate_end_year(cls, v, values):
        if v and v < values.get('startYear', 0):
            raise ValueError('End year must be after start year')
        return v

class Project(BaseModel):
    title: str
    description: str
    technologies: List[str] = []
    url: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    highlights: List[str] = []

class UserProfile(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    github: Optional[str] = None
    
    # Professional details
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    skills: List[str] = []
    certifications: List[str] = []
    languages: List[str] = []
    
    # Industry and role information
    industry: str
    current_role: Optional[str] = None
    years_experience: Optional[int] = None
    
    # Summary
    professional_summary: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v