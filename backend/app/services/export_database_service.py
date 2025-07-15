# app/services/export_database_service.py
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import logging

from app.core.firebase import db
from app.models.resume import (
    ExportRecord, BulkExportRecord, ExportStatus, ExportHistoryItem,
    ExportSummary, SubscriptionPlan
)
from app.exceptions.export_exceptions import (
    ExportNotFoundException, UnauthorizedExportAccessException,
    ResumeNotFoundException, ResumeDeletedExceptionException
)

logger = logging.getLogger(__name__)

class ExportDatabaseService:
    """Handles all database operations for exports"""
    
    async def create_export_record(self, export_data: ExportRecord) -> str:
        """Create a new export record in the database"""
        try:
            export_ref = db.collection("exports").document(export_data.id)
            export_ref.set(export_data.dict())
            logger.info(f"Created export record: {export_data.id}")
            return export_data.id
        except Exception as e:
            logger.error(f"Error creating export record {export_data.id}: {e}")
            raise
    
    async def get_export_record(self, export_id: str, user_id: Optional[str] = None) -> ExportRecord:
        """Get export record by ID with optional user verification"""
        try:
            export_ref = db.collection("exports").document(export_id)
            export_doc = export_ref.get()
            
            if not export_doc.exists:
                raise ExportNotFoundException(export_id)
            
            export_data = export_doc.to_dict()
            
            # Verify ownership if user_id provided
            if user_id and export_data.get("user_id") != user_id:
                raise UnauthorizedExportAccessException(export_id, user_id)
            
            return ExportRecord(**export_data)
            
        except (ExportNotFoundException, UnauthorizedExportAccessException):
            raise
        except Exception as e:
            logger.error(f"Error getting export record {export_id}: {e}")
            raise
    
    async def update_export_status(
        self, 
        export_id: str, 
        status: ExportStatus,
        file_size: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Update export status and related fields"""
        try:
            export_ref = db.collection("exports").document(export_id)
            updates = {
                "status": status.value,
                "updated_at": datetime.now()
            }
            
            if file_size is not None:
                updates["file_size"] = file_size
            
            if error_message:
                updates["error_message"] = error_message
            
            if status == ExportStatus.COMPLETED:
                updates["completed_at"] = datetime.now()
            
            export_ref.update(updates)
            logger.info(f"Updated export {export_id} status to {status.value}")
            
        except Exception as e:
            logger.error(f"Error updating export status for {export_id}: {e}")
            raise
    
    async def increment_download_count(self, export_id: str) -> None:
        """Increment download count for an export"""
        try:
            export_ref = db.collection("exports").document(export_id)
            export_doc = export_ref.get()
            
            if export_doc.exists:
                current_count = export_doc.to_dict().get("download_count", 0)
                export_ref.update({
                    "download_count": current_count + 1,
                    "last_downloaded_at": datetime.now()
                })
        except Exception as e:
            logger.warning(f"Could not update download count for {export_id}: {e}")
    
    async def get_user_export_history(
        self, 
        user_id: str, 
        limit: int = 50,
        include_expired: bool = False
    ) -> Tuple[List[ExportHistoryItem], ExportSummary]:
        """Get user's export history with summary"""
        try:
            # Build query
            query = db.collection("exports").where(
                "user_id", "==", user_id
            ).order_by(
                "created_at", direction="DESCENDING"
            ).limit(limit)
            
            exports = query.stream()
            export_history = []
            current_time = datetime.now()
            
            # Summary counters
            total_exports = 0
            completed_exports = 0
            total_downloads = 0
            total_size = 0
            
            for export_doc in exports:
                export_data = export_doc.to_dict()
                total_exports += 1
                
                is_expired = current_time > export_data.get("expires_at", datetime.min)
                
                # Skip expired exports if not requested
                if is_expired and not include_expired:
                    continue
                
                # Get resume title (handle deleted resumes)
                resume_title = await self._get_resume_title(export_data.get("resume_id", ""))
                
                # Check if can download
                can_download = (
                    export_data.get("status") == ExportStatus.COMPLETED.value and 
                    not is_expired
                )
                
                # Update summary
                if export_data.get("status") == ExportStatus.COMPLETED.value:
                    completed_exports += 1
                
                download_count = export_data.get("download_count", 0)
                total_downloads += download_count
                
                file_size = export_data.get("file_size", 0)
                if file_size:
                    total_size += file_size
                
                history_item = ExportHistoryItem(
                    id=export_data["id"],
                    resume_id=export_data["resume_id"],
                    resume_title=resume_title,
                    format=export_data["format"],
                    filename=export_data["filename"],
                    status=ExportStatus(export_data["status"]),
                    file_size=file_size,
                    download_count=download_count,
                    created_at=export_data["created_at"],
                    expires_at=export_data["expires_at"],
                    is_expired=is_expired,
                    can_download=can_download,
                    download_url=f"/api/v1/resume/export/{export_data['id']}/download" if can_download else None,
                    error_message=export_data.get("error_message")
                )
                
                export_history.append(history_item)
            
            summary = ExportSummary(
                total_exports=total_exports,
                completed_exports=completed_exports,
                total_downloads=total_downloads,
                total_size_bytes=total_size
            )
            
            return export_history, summary
            
        except Exception as e:
            logger.error(f"Error getting export history for user {user_id}: {e}")
            raise
    
    async def delete_export_record(self, export_id: str, user_id: str) -> None:
        """Delete export record after verifying ownership"""
        try:
            # First verify ownership
            await self.get_export_record(export_id, user_id)
            
            # Delete the record
            export_ref = db.collection("exports").document(export_id)
            export_ref.delete()
            logger.info(f"Deleted export record: {export_id}")
            
        except Exception as e:
            logger.error(f"Error deleting export record {export_id}: {e}")
            raise
    
    async def get_expired_exports(self, user_id: Optional[str] = None, limit: int = 100) -> List[ExportRecord]:
        """Get expired exports for cleanup"""
        try:
            current_time = datetime.now()
            query = db.collection("exports").where("expires_at", "<", current_time)
            
            if user_id:
                query = query.where("user_id", "==", user_id)
            
            query = query.limit(limit)
            expired_exports = query.stream()
            
            records = []
            for export_doc in expired_exports:
                try:
                    export_data = export_doc.to_dict()
                    records.append(ExportRecord(**export_data))
                except Exception as e:
                    logger.warning(f"Error parsing expired export record: {e}")
                    continue
            
            return records
            
        except Exception as e:
            logger.error(f"Error getting expired exports: {e}")
            return []
    
    async def cleanup_expired_exports(self, user_id: Optional[str] = None, batch_size: int = 100) -> int:
        """Clean up expired export records from database"""
        try:
            expired_exports = await self.get_expired_exports(user_id, batch_size)
            deleted_count = 0
            
            for export_record in expired_exports:
                try:
                    export_ref = db.collection("exports").document(export_record.id)
                    export_ref.delete()
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Could not delete export record {export_record.id}: {e}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during export cleanup: {e}")
            return 0
    
    # Bulk Export Methods
    
    async def create_bulk_export_record(self, bulk_export_data: BulkExportRecord) -> str:
        """Create a new bulk export record"""
        try:
            bulk_export_ref = db.collection("bulk_exports").document(bulk_export_data.id)
            bulk_export_ref.set(bulk_export_data.dict())
            logger.info(f"Created bulk export record: {bulk_export_data.id}")
            return bulk_export_data.id
        except Exception as e:
            logger.error(f"Error creating bulk export record {bulk_export_data.id}: {e}")
            raise
    
    async def get_bulk_export_record(self, bulk_export_id: str, user_id: Optional[str] = None) -> BulkExportRecord:
        """Get bulk export record by ID"""
        try:
            bulk_export_ref = db.collection("bulk_exports").document(bulk_export_id)
            bulk_export_doc = bulk_export_ref.get()
            
            if not bulk_export_doc.exists:
                raise ExportNotFoundException(bulk_export_id)
            
            bulk_export_data = bulk_export_doc.to_dict()
            
            # Verify ownership if user_id provided
            if user_id and bulk_export_data.get("user_id") != user_id:
                raise UnauthorizedExportAccessException(bulk_export_id, user_id)
            
            return BulkExportRecord(**bulk_export_data)
            
        except (ExportNotFoundException, UnauthorizedExportAccessException):
            raise
        except Exception as e:
            logger.error(f"Error getting bulk export record {bulk_export_id}: {e}")
            raise
    
    async def update_bulk_export_progress(
        self, 
        bulk_export_id: str, 
        status: ExportStatus,
        progress: int = 0,
        file_size: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Update bulk export progress and status"""
        try:
            bulk_export_ref = db.collection("bulk_exports").document(bulk_export_id)
            updates = {
                "status": status.value,
                "progress": progress,
                "updated_at": datetime.now()
            }
            
            if file_size is not None:
                updates["file_size"] = file_size
            
            if error_message:
                updates["error_message"] = error_message
            
            if status == ExportStatus.COMPLETED:
                updates["completed_at"] = datetime.now()
            
            bulk_export_ref.update(updates)
            logger.info(f"Updated bulk export {bulk_export_id}: status={status.value}, progress={progress}%")
            
        except Exception as e:
            logger.error(f"Error updating bulk export progress for {bulk_export_id}: {e}")
            raise
    
    async def increment_bulk_download_count(self, bulk_export_id: str) -> None:
        """Increment download count for a bulk export"""
        try:
            bulk_export_ref = db.collection("bulk_exports").document(bulk_export_id)
            bulk_export_doc = bulk_export_ref.get()
            
            if bulk_export_doc.exists:
                current_count = bulk_export_doc.to_dict().get("download_count", 0)
                bulk_export_ref.update({
                    "download_count": current_count + 1,
                    "last_downloaded_at": datetime.now()
                })
        except Exception as e:
            logger.warning(f"Could not update bulk download count for {bulk_export_id}: {e}")
    
    # Resume Validation Methods
    
    async def validate_resume_ownership(self, resume_id: str, user_id: str) -> Dict[str, Any]:
        """Validate that resume belongs to user and get resume data"""
        try:
            resume_ref = db.collection("resumes").document(resume_id)
            resume_doc = resume_ref.get()
            
            if not resume_doc.exists:
                raise ResumeNotFoundException(resume_id)
            
            resume_data = resume_doc.to_dict()
            
            if resume_data.get("user_id") != user_id:
                raise UnauthorizedExportAccessException(resume_id, user_id)
            
            if resume_data.get("deleted_at"):
                raise ResumeDeletedExceptionException(resume_id)
            
            return resume_data
            
        except (ResumeNotFoundException, UnauthorizedExportAccessException, ResumeDeletedExceptionException):
            raise
        except Exception as e:
            logger.error(f"Error validating resume ownership {resume_id}: {e}")
            raise
    
    async def validate_multiple_resume_ownership(self, resume_ids: List[str], user_id: str) -> List[Dict[str, Any]]:
        """Validate multiple resumes belong to user"""
        valid_resumes = []
        
        for resume_id in resume_ids:
            try:
                resume_data = await self.validate_resume_ownership(resume_id, user_id)
                valid_resumes.append(resume_data)
            except (ResumeNotFoundException, UnauthorizedExportAccessException, ResumeDeletedExceptionException):
                # Skip invalid resumes but continue with others
                logger.warning(f"Skipping invalid resume {resume_id} for user {user_id}")
                continue
        
        return valid_resumes
    
    async def update_resume_export_status(self, resume_id: str, is_subscribed: bool) -> None:
        """Update resume export status"""
        try:
            resume_ref = db.collection("resumes").document(resume_id)
            export_status = "subscribed" if is_subscribed else "paid"
            resume_ref.update({
                "export_status": export_status,
                "last_exported_at": datetime.now()
            })
        except Exception as e:
            logger.warning(f"Could not update resume export status for {resume_id}: {e}")
    
    # Helper Methods
    
    async def _get_resume_title(self, resume_id: str) -> str:
        """Get resume title with fallback for deleted resumes"""
        try:
            resume_ref = db.collection("resumes").document(resume_id)
            resume_doc = resume_ref.get()
            
            if resume_doc.exists:
                resume_data = resume_doc.to_dict()
                if resume_data.get("deleted_at"):
                    return f"{resume_data.get('title', 'Unknown Resume')} (Deleted)"
                else:
                    return resume_data.get("title", "Unknown Resume")
            else:
                return "Deleted Resume"
                
        except Exception as e:
            logger.warning(f"Could not get resume title for {resume_id}: {e}")
            return "Unknown Resume"
    
    async def get_export_statistics(self) -> Dict[str, Any]:
        """Get platform-wide export statistics (admin only)"""
        try:
            current_time = datetime.now()
            thirty_days_ago = current_time - timedelta(days=30)
            
            # Get all exports
            all_exports = list(db.collection("exports").stream())
            recent_exports = [
                exp for exp in all_exports 
                if exp.to_dict().get("created_at", datetime.min) >= thirty_days_ago
            ]
            
            # Calculate statistics
            stats = {
                "total_exports": len(all_exports),
                "recent_exports_30d": len(recent_exports),
                "by_status": {"processing": 0, "completed": 0, "failed": 0},
                "by_format": {"pdf": 0, "docx": 0},
                "by_plan": {"free": 0, "premium": 0, "enterprise": 0},
                "total_file_size": 0,
                "average_file_size": 0,
                "expired_exports": 0
            }
            
            total_size = 0
            completed_count = 0
            
            for export_doc in all_exports:
                export_data = export_doc.to_dict()
                
                # Count by status
                status = export_data.get("status", "unknown")
                if status in stats["by_status"]:
                    stats["by_status"][status] += 1
                
                # Count by format
                format_type = export_data.get("format", "unknown")
                if format_type in stats["by_format"]:
                    stats["by_format"][format_type] += 1
                
                # Count by plan
                plan = export_data.get("subscription_plan", "free")
                if plan in stats["by_plan"]:
                    stats["by_plan"][plan] += 1
                
                # File size statistics
                file_size = export_data.get("file_size", 0)
                if file_size > 0:
                    total_size += file_size
                    completed_count += 1
                
                # Check if expired
                expires_at = export_data.get("expires_at")
                if expires_at and current_time > expires_at:
                    stats["expired_exports"] += 1
            
            stats["total_file_size"] = total_size
            stats["average_file_size"] = round(total_size / completed_count, 2) if completed_count > 0 else 0
            
            # Get bulk export statistics
            bulk_exports = list(db.collection("bulk_exports").stream())
            
            return {
                "exports": stats,
                "bulk_exports": {
                    "total": len(bulk_exports),
                    "recent_30d": len([
                        exp for exp in bulk_exports 
                        if exp.to_dict().get("created_at", datetime.min) >= thirty_days_ago
                    ])
                },
                "generated_at": current_time
            }
            
        except Exception as e:
            logger.error(f"Error getting export statistics: {e}")
            raise

# Global database service instance
export_db_service = ExportDatabaseService()