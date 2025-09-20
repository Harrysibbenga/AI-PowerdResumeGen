# app/models/export.py
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import validator, Field
import re
from .base import BaseModel, ExportFormat, ExportStatus, SubscriptionPlan

class ExportRequest(BaseModel):
    format: ExportFormat
    content: Dict[str, Any]
    filename: Optional[str] = None
    
    @validator('filename')
    def validate_filename(cls, v):
        if v is not None:
            # Sanitize filename
            safe_filename = re.sub(r'[^\w\s\-_\.]', '', v)
            if len(safe_filename) > 100:
                safe_filename = safe_filename[:100]
            return safe_filename
        return v

class ExportResponse(BaseModel):
    download_url: str
    filename: str
    message: str
    expires_at: Optional[datetime] = None

class ExportRecord(BaseModel):
    id: str
    user_id: str
    resume_id: str
    resume_title: str
    format: ExportFormat
    filename: str
    file_path: str
    status: ExportStatus
    subscription_plan: SubscriptionPlan
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: datetime
    download_count: int = 0
    last_downloaded_at: Optional[datetime] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None

class BulkExportRequest(BaseModel):
    resume_ids: List[str] = Field(..., min_items=1, max_items=20)
    format: ExportFormat
    
    @validator('resume_ids')
    def validate_resume_ids(cls, v):
        if len(set(v)) != len(v):
            raise ValueError("Duplicate resume IDs are not allowed")
        return v

class BulkExportRecord(BaseModel):
    id: str
    user_id: str
    resume_ids: List[str]
    valid_resume_count: int
    format: ExportFormat
    zip_path: str
    status: ExportStatus
    progress: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: datetime
    download_count: int = 0
    last_downloaded_at: Optional[datetime] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None

class ExportLimits(BaseModel):
    monthly_exports: int
    file_size_mb: int
    export_expiry_hours: int
    bulk_export_enabled: bool = False
    max_bulk_resumes: int = 20

class SubscriptionInfo(BaseModel):
    is_subscribed: bool
    plan: SubscriptionPlan
    expires_at: Optional[datetime] = None
    features: List[str] = []

class ExportUsage(BaseModel):
    monthly_exports: int
    monthly_remaining: int
    can_export: bool
    limit_reason: Optional[str] = None

class ExportLimitCheck(BaseModel):
    can_export: bool
    reason: str
    limit: Optional[int] = None
    used: Optional[int] = None
    remaining: Optional[int] = None

class ExportHistoryItem(BaseModel):
    id: str
    resume_id: str
    resume_title: str
    format: ExportFormat
    filename: str
    status: ExportStatus
    file_size: Optional[int] = None
    download_count: int
    created_at: datetime
    expires_at: datetime
    is_expired: bool
    can_download: bool
    download_url: Optional[str] = None
    error_message: Optional[str] = None

class ExportSummary(BaseModel):
    total_exports: int
    completed_exports: int
    total_downloads: int
    total_size_bytes: int

class CleanupResult(BaseModel):
    message: str
    deleted_count: int
    deleted_size_bytes: int
    deleted_size_mb: float