# app/services/export_business_logic.py
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging

from app.models.resume import (
    ExportRequest, ExportResponse, ExportRecord, ExportFormat, ExportStatus,
    BulkExportRequest, BulkExportRecord, SubscriptionPlan, ExportHistoryItem,
    ExportSummary, CleanupResult
)
from app.services.subscription_service import subscription_service
from app.services.export_database_service import export_db_service
from app.services.file_manager import file_manager
from app.services.export_processor import export_processor
from app.core.export_config import export_config
from app.exceptions.export_exceptions import (
    ExportLimitExceededException, PremiumFeatureRequiredException,
    BulkExportLimitException, ExportNotFoundException, ExportExpiredException,
    ExportProcessingException, ExportFailedException, UnauthorizedExportAccessException
)

logger = logging.getLogger(__name__)

class ExportBusinessLogic:
    """Main business logic service for export operations"""
    
    def __init__(self):
        self.config = export_config
    
    async def create_export(
        self, 
        resume_id: str, 
        user_id: str, 
        request: ExportRequest
    ) -> ExportResponse:
        """Create a new export job"""
        
        # Get user subscription and validate limits
        subscription = await subscription_service.get_user_subscription(user_id)
        limit_check = await subscription_service.check_export_limits(user_id, subscription)
        
        if not limit_check.can_export:
            if limit_check.reason == "limit_reached":
                raise ExportLimitExceededException(
                    limit_check.limit, limit_check.used, subscription.plan.value
                )
        
        # Validate resume ownership and get data
        resume_data = await export_db_service.validate_resume_ownership(resume_id, user_id)
        
        # Generate export ID and file path
        export_id = f"{resume_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        file_path = file_manager.generate_export_path(user_id, resume_id, request.format.value)
        
        # Generate filename
        filename = self._generate_filename(resume_data, request)
        
        # Create export record
        export_record = ExportRecord(
            id=export_id,
            user_id=user_id,
            resume_id=resume_id,
            resume_title=resume_data.get("title", "Resume"),
            format=request.format,
            filename=filename,
            file_path=file_path,
            status=ExportStatus.PROCESSING,
            subscription_plan=subscription.plan,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=self.config.EXPORT_EXPIRY_HOURS)
        )
        
        # Save to database
        await export_db_service.create_export_record(export_record)
        
        # Update usage tracking
        await subscription_service.increment_export_usage(user_id)
        
        # Update resume export status
        await export_db_service.update_resume_export_status(resume_id, subscription.is_subscribed)
        
        # Start background processing (this would be handled by a task queue in production)
        # For now, we'll return the response and process asynchronously
        
        return ExportResponse(
            download_url=f"/api/v1/resume/export/{export_id}/download",
            filename=filename,
            message="export_started",
            expires_at=export_record.expires_at
        )
    
    async def start_export_processing(
        self, 
        export_id: str, 
        resume_data: Dict[str, Any], 
        content: Dict[str, Any],
        format_type: ExportFormat
    ) -> None:
        """Start the actual export processing (for background tasks)"""
        try:
            export_record = await export_db_service.get_export_record(export_id)
            
            success = await export_processor.process_single_export(
                export_id, resume_data, content, export_record.file_path, format_type
            )
            
            if not success:
                logger.error(f"Export processing failed for {export_id}")
                
        except Exception as e:
            logger.error(f"Error in export processing for {export_id}: {e}")
            await export_db_service.update_export_status(
                export_id, ExportStatus.FAILED, error_message=str(e)
            )
    
    async def get_download_info(self, export_id: str, user_id: str) -> Tuple[str, str, str]:
        """Get download information for an export"""
        
        # Get and validate export record
        export_record = await export_db_service.get_export_record(export_id, user_id)
        
        # Check if expired
        if datetime.now() > export_record.expires_at:
            raise ExportExpiredException(export_id)
        
        # Check status
        if export_record.status == ExportStatus.PROCESSING:
            raise ExportProcessingException(export_id)
        elif export_record.status == ExportStatus.FAILED:
            raise ExportFailedException(export_id, export_record.error_message)
        elif export_record.status != ExportStatus.COMPLETED:
            raise ExportProcessingException(export_id)
        
        # Check if file exists
        if not file_manager.file_exists(export_record.file_path):
            raise ExportNotFoundException(export_id)
        
        # Update download count
        await export_db_service.increment_download_count(export_id)
        
        # Determine media type
        media_type = (
            "application/pdf" if export_record.format == ExportFormat.PDF 
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        return export_record.file_path, export_record.filename, media_type
    
    async def get_export_status(self, export_id: str, user_id: str) -> Dict[str, Any]:
        """Get export status with progress information"""
        
        export_record = await export_db_service.get_export_record(export_id, user_id)
        
        # Calculate progress percentage
        progress = 0
        if export_record.status == ExportStatus.PROCESSING:
            progress = 50
        elif export_record.status == ExportStatus.COMPLETED:
            progress = 100
        elif export_record.status == ExportStatus.FAILED:
            progress = 0
        
        return {
            "id": export_record.id,
            "status": export_record.status.value,
            "progress": progress,
            "filename": export_record.filename,
            "format": export_record.format.value,
            "file_size": export_record.file_size,
            "created_at": export_record.created_at,
            "expires_at": export_record.expires_at,
            "download_count": export_record.download_count,
            "error_message": export_record.error_message,
            "is_expired": datetime.now() > export_record.expires_at,
            "download_url": (
                f"/api/v1/resume/export/{export_id}/download" 
                if export_record.status == ExportStatus.COMPLETED and datetime.now() <= export_record.expires_at 
                else None
            )
        }
    
    async def get_user_export_history(
        self, 
        user_id: str, 
        limit: int = 50,
        include_expired: bool = False
    ) -> Dict[str, Any]:
        """Get user's export history with summary"""
        
        export_history, summary = await export_db_service.get_user_export_history(
            user_id, limit, include_expired
        )
        
        return {
            "exports": [item.dict() for item in export_history],
            "summary": summary.dict()
        }
    
    async def delete_export(self, export_id: str, user_id: str) -> Dict[str, str]:
        """Delete an export file and record"""
        
        # Get export record (validates ownership)
        export_record = await export_db_service.get_export_record(export_id, user_id)
        
        # Delete physical file if it exists
        if file_manager.file_exists(export_record.file_path):
            file_manager.delete_file(export_record.file_path)
        
        # Delete database record
        await export_db_service.delete_export_record(export_id, user_id)
        
        return {"message": "Export deleted successfully"}
    
    # Bulk Export Methods
    
    async def create_bulk_export(
        self, 
        user_id: str, 
        request: BulkExportRequest
    ) -> Dict[str, Any]:
        """Create a bulk export job"""
        
        # Check subscription and permissions
        subscription = await subscription_service.get_user_subscription(user_id)
        
        if not subscription.is_subscribed:
            raise PremiumFeatureRequiredException("Bulk export")
        
        # Validate bulk export permissions
        can_bulk_export = await subscription_service.validate_bulk_export_permission(
            user_id, len(request.resume_ids)
        )
        
        if not can_bulk_export:
            limits = self.config.subscription_limits.get(subscription.plan)
            max_allowed = limits.max_bulk_resumes if limits else 0
            raise BulkExportLimitException(len(request.resume_ids), max_allowed)
        
        # Validate resume ownership
        valid_resumes = await export_db_service.validate_multiple_resume_ownership(
            request.resume_ids, user_id
        )
        
        if not valid_resumes:
            raise ExportNotFoundException("No valid resumes found")
        
        # Generate bulk export ID and file path
        bulk_export_id = f"bulk_{user_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        zip_path = file_manager.generate_bulk_export_path(user_id, request.format.value)
        
        # Create bulk export record
        bulk_export_record = BulkExportRecord(
            id=bulk_export_id,
            user_id=user_id,
            resume_ids=request.resume_ids,
            valid_resume_count=len(valid_resumes),
            format=request.format,
            zip_path=zip_path,
            status=ExportStatus.PROCESSING,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=self.config.BULK_EXPORT_EXPIRY_HOURS)
        )
        
        # Save to database
        await export_db_service.create_bulk_export_record(bulk_export_record)
        
        # Start background processing (would be a task queue in production)
        
        return {
            "bulk_export_id": bulk_export_id,
            "message": "Bulk export started",
            "resume_count": len(valid_resumes),
            "download_url": f"/api/v1/resume/export/bulk/{bulk_export_id}/download",
            "expires_at": bulk_export_record.expires_at
        }
    
    async def start_bulk_export_processing(
        self, 
        bulk_export_id: str, 
        resumes: List[Dict[str, Any]], 
        format_type: ExportFormat
    ) -> None:
        """Start bulk export processing (for background tasks)"""
        try:
            bulk_export_record = await export_db_service.get_bulk_export_record(bulk_export_id)
            
            success = await export_processor.process_bulk_export(
                bulk_export_id, resumes, format_type, bulk_export_record.zip_path
            )
            
            if not success:
                logger.error(f"Bulk export processing failed for {bulk_export_id}")
                
        except Exception as e:
            logger.error(f"Error in bulk export processing for {bulk_export_id}: {e}")
            await export_db_service.update_bulk_export_progress(
                bulk_export_id, ExportStatus.FAILED, 0, error_message=str(e)
            )
    
    async def get_bulk_download_info(self, bulk_export_id: str, user_id: str) -> Tuple[str, str]:
        """Get bulk export download information"""
        
        # Get and validate bulk export record
        bulk_export_record = await export_db_service.get_bulk_export_record(bulk_export_id, user_id)
        
        # Check if expired
        if datetime.now() > bulk_export_record.expires_at:
            raise ExportExpiredException(bulk_export_id)
        
        # Check status
        if bulk_export_record.status == ExportStatus.PROCESSING:
            raise ExportProcessingException(bulk_export_id)
        elif bulk_export_record.status == ExportStatus.FAILED:
            raise ExportFailedException(bulk_export_id, bulk_export_record.error_message)
        elif bulk_export_record.status != ExportStatus.COMPLETED:
            raise ExportProcessingException(bulk_export_id)
        
        # Check if file exists
        if not file_manager.file_exists(bulk_export_record.zip_path):
            raise ExportNotFoundException(bulk_export_id)
        
        # Update download count
        await export_db_service.increment_bulk_download_count(bulk_export_id)
        
        # Generate filename
        timestamp = bulk_export_record.created_at.strftime("%Y%m%d")
        filename = f"resumes_bulk_export_{timestamp}.zip"
        
        return bulk_export_record.zip_path, filename
    
    async def get_bulk_export_status(self, bulk_export_id: str, user_id: str) -> Dict[str, Any]:
        """Get bulk export status"""
        
        bulk_export_record = await export_db_service.get_bulk_export_record(bulk_export_id, user_id)
        
        return {
            "id": bulk_export_record.id,
            "status": bulk_export_record.status.value,
            "progress": bulk_export_record.progress,
            "resume_count": bulk_export_record.valid_resume_count,
            "format": bulk_export_record.format.value,
            "file_size": bulk_export_record.file_size,
            "created_at": bulk_export_record.created_at,
            "expires_at": bulk_export_record.expires_at,
            "download_count": bulk_export_record.download_count,
            "error_message": bulk_export_record.error_message,
            "is_expired": datetime.now() > bulk_export_record.expires_at,
            "download_url": (
                f"/api/v1/resume/export/bulk/{bulk_export_id}/download" 
                if bulk_export_record.status == ExportStatus.COMPLETED and datetime.now() <= bulk_export_record.expires_at 
                else None
            )
        }
    
    # Cleanup and Admin Methods
    
    async def cleanup_user_exports(self, user_id: str) -> CleanupResult:
        """Clean up expired exports for a specific user"""
        
        # Get expired exports
        expired_exports = await export_db_service.get_expired_exports(user_id)
        
        # Clean up files
        file_paths = [export.file_path for export in expired_exports]
        files_deleted, bytes_freed = file_manager.cleanup_expired_files(file_paths)
        
        # Clean up database records
        db_deleted = await export_db_service.cleanup_expired_exports(user_id)
        
        return CleanupResult(
            message=f"Cleaned up {files_deleted} expired exports",
            deleted_count=files_deleted,
            deleted_size_bytes=bytes_freed,
            deleted_size_mb=round(bytes_freed / (1024 * 1024), 2)
        )
    
    async def get_export_limits_info(self, user_id: str) -> Dict[str, Any]:
        """Get user's export limits and current usage"""
        
        # Get subscription info
        subscription = await subscription_service.get_user_subscription(user_id)
        limits = self.config.subscription_limits.get(subscription.plan)
        
        if not limits:
            return {"error": "Invalid subscription plan"}
        
        # Get current usage
        monthly_usage = await subscription_service.get_monthly_usage(user_id)
        
        return {
            "subscription": {
                "plan": subscription.plan.value,
                "is_subscribed": subscription.is_subscribed,
                "expires_at": subscription.expires_at
            },
            "limits": {
                "monthly_exports": "unlimited" if limits.monthly_exports == -1 else limits.monthly_exports,
                "file_size_mb": limits.file_size_mb,
                "export_expiry_hours": limits.export_expiry_hours,
                "bulk_export_enabled": limits.bulk_export_enabled,
                "max_bulk_resumes": limits.max_bulk_resumes
            },
            "current_usage": {
                "monthly_exports": monthly_usage,
                "monthly_remaining": (
                    "unlimited" if limits.monthly_exports == -1 
                    else max(0, limits.monthly_exports - monthly_usage)
                ),
                "can_export": monthly_usage < limits.monthly_exports if limits.monthly_exports != -1 else True
            }
        }
    
    async def admin_cleanup_all_expired(self, admin_user_id: str) -> CleanupResult:
        """Admin function to clean up all expired exports"""
        
        # Verify admin privileges
        is_admin = await subscription_service.is_admin_user(admin_user_id)
        if not is_admin:
            raise UnauthorizedExportAccessException("admin_cleanup", admin_user_id)
        
        # Get all expired exports
        expired_exports = await export_db_service.get_expired_exports()
        
        # Clean up files
        file_paths = [export.file_path for export in expired_exports]
        files_deleted, bytes_freed = file_manager.cleanup_expired_files(file_paths)
        
        # Clean up database records
        db_deleted = await export_db_service.cleanup_expired_exports()
        
        return CleanupResult(
            message=f"Admin cleanup completed: {files_deleted} expired exports removed",
            deleted_count=files_deleted,
            deleted_size_bytes=bytes_freed,
            deleted_size_mb=round(bytes_freed / (1024 * 1024), 2)
        )
    
    async def get_admin_statistics(self, admin_user_id: str) -> Dict[str, Any]:
        """Get platform-wide export statistics (admin only)"""
        
        # Verify admin privileges
        is_admin = await subscription_service.is_admin_user(admin_user_id)
        if not is_admin:
            raise UnauthorizedExportAccessException("admin_stats", admin_user_id)
        
        return await export_db_service.get_export_statistics()
    
    # Helper Methods
    
    def _generate_filename(self, resume_data: Dict[str, Any], request: ExportRequest) -> str:
        """Generate safe filename for export"""
        if request.filename:
            return request.filename
        
        # Generate from resume title
        safe_title = ''.join(c for c in resume_data.get('title', 'resume') if c.isalnum() or c in (' ', '-', '_'))
        safe_title = safe_title.replace(' ', '_')[:50]
        
        if not safe_title:
            safe_title = "resume"
        
        return f"{safe_title}.{request.format.value}"

# Global business logic service instance
export_business_logic = ExportBusinessLogic()