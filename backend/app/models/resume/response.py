from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import ExportStatus, ResumeTone, ResumeLength, ResumeTemplate

class ResumeResponse(BaseModel):
    id: str
    title: str
    target_job_title: str
    target_job_role: Optional[str] = None
    sections: Dict[str, Any]
    message: str
    created_at: datetime
    
    # Summary for card display (50 words max)
    summary_excerpt: Optional[str] = None
    
    # Metadata for frontend
    industry: str
    template_id: ResumeTemplate
    export_status: ExportStatus = ExportStatus.FREE

class ResumeListItem(BaseModel):
    id: str
    title: str
    target_job_title: str
    target_job_role: Optional[str] = None
    target_company: Optional[str] = None
    industry: str
    template_id: ResumeTemplate
    export_status: ExportStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Summary excerpt for card display
    summary_excerpt: Optional[str] = None
    
    # Quick stats for cards
    sections_count: int = 0
    word_count: Optional[int] = None
    
class ResumeListResponse(BaseModel):
    resumes: List[ResumeListItem]
    total: int
    page: int = 1
    per_page: int = 10
    has_next: bool = False
    has_prev: bool = False

class ExportRequest(BaseModel):
    resumeId: str
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