# app/routers/export_router.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from typing import Dict, List
import logging

from app.dependencies.auth_dependencies import get_current_user
from app.models.resume import ExportRequest, ExportResponse, BulkExportRequest
from app.services.export_business_logic import export_business_logic
from app.exceptions.export_exceptions import (
    ExportBaseException, ExportLimitExceededException, ExportNotFoundException,
    ExportExpiredException, ExportProcessingException, ExportFailedException,
    UnauthorizedExportAccessException, PremiumFeatureRequiredException,
    BulkExportLimitException, ResumeNotFoundException, ResumeDeletedExceptionException
)

router = APIRouter(prefix="/export", tags=["exports"])
logger = logging.getLogger(__name__)

# Exception handler mapping
def handle_export_exception(e: ExportBaseException) -> HTTPException:
    """Convert export exceptions to HTTP exceptions"""
    
    exception_mapping = {
        "EXPORT_LIMIT_EXCEEDED": (403, "Export limit exceeded"),
        "EXPORT_NOT_FOUND": (404, "Export not found"),
        "EXPORT_EXPIRED": (410, "Export has expired"),
        "EXPORT_PROCESSING": (202, "Export is still processing"),
        "EXPORT_FAILED": (500, "Export failed"),
        "UNAUTHORIZED_EXPORT_ACCESS": (403, "Unauthorized access"),
        "PREMIUM_FEATURE_REQUIRED": (403, "Premium feature required"),
        "BULK_EXPORT_LIMIT_EXCEEDED": (400, "Bulk export limit exceeded"),
        "RESUME_NOT_FOUND": (404, "Resume not found"),
        "RESUME_DELETED": (410, "Resume has been deleted"),
        "FILE_SIZE_EXCEEDED": (413, "File size exceeds limit"),
        "INVALID_EXPORT_FORMAT": (400, "Invalid export format"),
        "FILE_SYSTEM_ERROR": (500, "File system error")
    }
    
    status_code, default_message = exception_mapping.get(e.error_code, (500, "Internal server error"))
    return HTTPException(status_code=status_code, detail=e.message)

# Individual Export Endpoints

@router.post("/{resume_id}", response_model=ExportResponse)
async def create_export(
    resume_id: str,
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(get_current_user)
):
    """Create a new export job for a resume"""
    try:
        user_id = user["uid"]
        
        # Create export job
        response = await export_business_logic.create_export(resume_id, user_id, request)
        
        # Start background processing
        # In production, this would be handled by a proper task queue (Celery, RQ, etc.)
        # For now, we'll use FastAPI's BackgroundTasks
        background_tasks.add_task(
            start_export_background_task,
            response.download_url.split("/")[-2],  # Extract export_id from URL
            resume_id,
            user_id,
            request
        )
        
        return response
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error creating export for resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def start_export_background_task(
    export_id: str, 
    resume_id: str, 
    user_id: str, 
    request: ExportRequest
):
    """Background task to start export processing"""
    try:
        # Get resume data
        from app.services.export_database_service import export_db_service
        resume_data = await export_db_service.validate_resume_ownership(resume_id, user_id)
        
        # Start processing
        await export_business_logic.start_export_processing(
            export_id, resume_data, request.content, request.format
        )
        
    except Exception as e:
        logger.error(f"Background export processing failed for {export_id}: {e}")

@router.get("/{export_id}/download")
async def download_export(
    export_id: str, 
    user: Dict = Depends(get_current_user)
):
    """Download an exported resume file"""
    try:
        user_id = user["uid"]
        
        file_path, filename, media_type = await export_business_logic.get_download_info(
            export_id, user_id
        )
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error downloading export {export_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{export_id}/status")
async def get_export_status(
    export_id: str, 
    user: Dict = Depends(get_current_user)
):
    """Get the status of an export job"""
    try:
        user_id = user["uid"]
        return await export_business_logic.get_export_status(export_id, user_id)
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error getting export status {export_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{export_id}")
async def delete_export(
    export_id: str, 
    user: Dict = Depends(get_current_user)
):
    """Delete an export file and record"""
    try:
        user_id = user["uid"]
        return await export_business_logic.delete_export(export_id, user_id)
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error deleting export {export_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Bulk Export Endpoints

@router.post("/bulk")
async def create_bulk_export(
    request: BulkExportRequest,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(get_current_user)
):
    """Create a bulk export job for multiple resumes (Premium feature)"""
    try:
        user_id = user["uid"]
        
        # Create bulk export job
        response = await export_business_logic.create_bulk_export(user_id, request)
        
        # Start background processing
        background_tasks.add_task(
            start_bulk_export_background_task,
            response["bulk_export_id"],
            request.resume_ids,
            user_id,
            request.format
        )
        
        return response
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error creating bulk export: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def start_bulk_export_background_task(
    bulk_export_id: str,
    resume_ids: List[str],
    user_id: str,
    format_type
):
    """Background task to start bulk export processing"""
    try:
        # Get valid resumes
        from app.services.export_database_service import export_db_service
        valid_resumes = await export_db_service.validate_multiple_resume_ownership(
            resume_ids, user_id
        )
        
        # Start processing
        await export_business_logic.start_bulk_export_processing(
            bulk_export_id, valid_resumes, format_type
        )
        
    except Exception as e:
        logger.error(f"Background bulk export processing failed for {bulk_export_id}: {e}")

@router.get("/bulk/{bulk_export_id}/download")
async def download_bulk_export(
    bulk_export_id: str, 
    user: Dict = Depends(get_current_user)
):
    """Download bulk export ZIP file"""
    try:
        user_id = user["uid"]
        
        zip_path, filename = await export_business_logic.get_bulk_download_info(
            bulk_export_id, user_id
        )
        
        return FileResponse(
            path=zip_path,
            filename=filename,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error downloading bulk export {bulk_export_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/bulk/{bulk_export_id}/status")
async def get_bulk_export_status(
    bulk_export_id: str, 
    user: Dict = Depends(get_current_user)
):
    """Get status of bulk export"""
    try:
        user_id = user["uid"]
        return await export_business_logic.get_bulk_export_status(bulk_export_id, user_id)
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error getting bulk export status {bulk_export_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User Management Endpoints

@router.get("/history")
async def get_export_history(
    user: Dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    include_expired: bool = Query(False)
):
    """Get user's export history"""
    try:
        user_id = user["uid"]
        return await export_business_logic.get_user_export_history(
            user_id, limit, include_expired
        )
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error getting export history for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/limits")
async def get_export_limits(user: Dict = Depends(get_current_user)):
    """Get user's export limits and current usage"""
    try:
        user_id = user["uid"]
        return await export_business_logic.get_export_limits_info(user_id)
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error getting export limits for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/cleanup-expired")
async def cleanup_expired_exports(user: Dict = Depends(get_current_user)):
    """Clean up expired export files for the current user"""
    try:
        user_id = user["uid"]
        result = await export_business_logic.cleanup_user_exports(user_id)
        return result.dict()
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error cleaning up exports for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Admin Endpoints

@router.post("/admin/cleanup-all-expired")
async def admin_cleanup_expired_exports(user: Dict = Depends(get_current_user)):
    """Admin endpoint to clean up all expired exports (requires admin role)"""
    try:
        user_id = user["uid"]
        result = await export_business_logic.admin_cleanup_all_expired(user_id)
        return result.dict()
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error in admin cleanup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/admin/stats")
async def get_export_statistics(user: Dict = Depends(get_current_user)):
    """Get platform-wide export statistics (admin only)"""
    try:
        user_id = user["uid"]
        return await export_business_logic.get_admin_statistics(user_id)
        
    except ExportBaseException as e:
        raise handle_export_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error getting export statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")