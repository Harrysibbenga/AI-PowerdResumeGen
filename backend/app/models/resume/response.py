from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import ResumeTemplate, ExportStatus, BaseModel

class ResumeResponse(BaseModel):
    id: str
    title: str
    target_job_title: str
    target_job_role: Optional[str] = None
    target_company: Optional[str] = None
    industry: str

    template_id: ResumeTemplate
    export_status: ExportStatus

    profile_data: Optional[Dict[str, Any]] = None
    sections: Dict[str, Any]
    version: Optional[int] = 1
    summary_excerpt: Optional[str] = None

    sections_count: Optional[int] = None
    word_count: Optional[int] = None
    
     # Section inclusion flags
    include_projects: bool = True  
    include_certifications: bool = True  
    include_languages: bool = True  

    created_at: datetime
    updated_at: Optional[datetime] = None

class ResumeListItem(BaseModel):
    id: str
    title: str
    target_job_title: str
    target_job_role: Optional[str] = None
    target_company: Optional[str] = None
    industry: str

    template_id: ResumeTemplate
    export_status: ExportStatus

    summary_excerpt: Optional[str] = None
    sections_count: int = 0
    word_count: Optional[int] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

class ResumeListResponse(BaseModel):
    resumes: List[ResumeListItem]
    total: int
    page: int = 1
    per_page: int = 10
    has_next: bool = False
    has_prev: bool = False

class ExportRequest(BaseModel):
    resume_id: str
    format: str  # "pdf" or "docx"
    content: Dict[str, Any]
    filename: Optional[str] = None

class ExportResponse(BaseModel):
    download_url: str
    filename: str
    message: str
    expires_at: Optional[datetime] = None

class ResumeStats(BaseModel):
    total_resumes: int
    total_exports: int
    industries: Dict[str, int]
    templates: Dict[str, int]
    recent_activity: List[Dict[str, Any]]
