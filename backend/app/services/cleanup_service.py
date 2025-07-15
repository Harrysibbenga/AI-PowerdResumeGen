# app/services/cleanup_service.py
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
import schedule
import time
from threading import Thread

from app.services.export_database_service import export_db_service
from app.services.file_manager import file_manager
from app.services.export_processor import export_processor
from app.core.export_config import export_config
from app.models.resume import CleanupResult

logger = logging.getLogger(__name__)

class CleanupService:
    """Service for automated cleanup and maintenance tasks"""
    
    def __init__(self):
        self.config = export_config
        self.running = False
        self.cleanup_thread = None
    
    def start_scheduler(self):
        """Start the cleanup scheduler in a background thread"""
        if self.running:
            return
        
        self.running = True
        
        # Schedule cleanup tasks
        schedule.every(1).hours.do(self._run_async_task, self.cleanup_expired_exports)
        schedule.every(6).hours.do(self._run_async_task, self.cleanup_failed_exports)
        schedule.every().day.at("02:00").do(self._run_async_task, self.cleanup_orphaned_files)
        schedule.every().week.do(self._run_async_task, self.cleanup_old_usage_records)
        
        # Start scheduler thread
        self.cleanup_thread = Thread(target=self._run_scheduler, daemon=True)
        self.cleanup_thread.start()
        
        logger.info("Cleanup scheduler started")
    
    def stop_scheduler(self):
        """Stop the cleanup scheduler"""
        self.running = False
        schedule.clear()
        logger.info("Cleanup scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in cleanup scheduler: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _run_async_task(self, coro_func):
        """Helper to run async functions in scheduler"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro_func())
            loop.close()
        except Exception as e:
            logger.error(f"Error running async cleanup task: {e}")
    
    async def cleanup_expired_exports(self) -> CleanupResult:
        """Clean up expired exports"""
        try:
            logger.info("Starting cleanup of expired exports")
            
            # Get expired exports in batches
            batch_size = self.config.CLEANUP_BATCH_SIZE
            total_deleted = 0
            total_bytes_freed = 0
            
            while True:
                expired_exports = await export_db_service.get_expired_exports(limit=batch_size)
                
                if not expired_exports:
                    break
                
                # Clean up files
                file_paths = [export.file_path for export in expired_exports]
                files_deleted, bytes_freed = file_manager.cleanup_expired_files(file_paths)
                
                # Clean up database records
                for export_record in expired_exports:
                    try:
                        await export_db_service.delete_export_record(
                            export_record.id, export_record.user_id
                        )
                    except Exception as e:
                        logger.warning(f"Failed to delete export record {export_record.id}: {e}")
                
                total_deleted += files_deleted
                total_bytes_freed += bytes_freed
                
                # If we got fewer than batch_size, we're done
                if len(expired_exports) < batch_size:
                    break
            
            # Clean up expired bulk exports
            bulk_deleted, bulk_bytes_freed = await self._cleanup_expired_bulk_exports()
            total_deleted += bulk_deleted
            total_bytes_freed += bulk_bytes_freed
            
            result = CleanupResult(
                message=f"Cleaned up {total_deleted} expired exports",
                deleted_count=total_deleted,
                deleted_size_bytes=total_bytes_freed,
                deleted_size_mb=round(total_bytes_freed / (1024 * 1024), 2)
            )
            
            logger.info(f"Expired export cleanup completed: {result.message}")
            return result
            
        except Exception as e:
            logger.error(f"Error during expired export cleanup: {e}")
            return CleanupResult(
                message=f"Cleanup failed: {str(e)}",
                deleted_count=0,
                deleted_size_bytes=0,
                deleted_size_mb=0
            )
    
    async def _cleanup_expired_bulk_exports(self) -> tuple[int, int]:
        """Clean up expired bulk exports"""
        try:
            from app.core.firebase import db
            
            current_time = datetime.now()
            expired_bulk_exports = db.collection("bulk_exports").where(
                "expires_at", "<", current_time
            ).limit(self.config.CLEANUP_BATCH_SIZE).stream()
            
            deleted_count = 0
            bytes_freed = 0
            
            for bulk_export_doc in expired_bulk_exports:
                try:
                    bulk_export_data = bulk_export_doc.to_dict()
                    zip_path = bulk_export_data.get("zip_path")
                    
                    # Delete ZIP file
                    if zip_path and file_manager.file_exists(zip_path):
                        file_size = file_manager.get_file_size(zip_path)
                        file_manager.delete_file(zip_path)
                        bytes_freed += file_size
                    
                    # Delete record
                    bulk_export_doc.reference.delete()
                    deleted_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to cleanup bulk export record: {e}")
            
            return deleted_count, bytes_freed
            
        except Exception as e:
            logger.error(f"Error cleaning up bulk exports: {e}")
            return 0, 0
    
    async def cleanup_failed_exports(self) -> CleanupResult:
        """Clean up old failed exports"""
        try:
            logger.info("Starting cleanup of failed exports")
            
            deleted_count = await export_processor.cleanup_failed_exports(
                max_age_hours=self.config.EXPORT_EXPIRY_HOURS * 2
            )
            
            result = CleanupResult(
                message=f"Cleaned up {deleted_count} failed exports",
                deleted_count=deleted_count,
                deleted_size_bytes=0,  # Size not tracked for failed exports
                deleted_size_mb=0
            )
            
            logger.info(f"Failed export cleanup completed: {result.message}")
            return result
            
        except Exception as e:
            logger.error(f"Error during failed export cleanup: {e}")
            return CleanupResult(
                message=f"Failed export cleanup failed: {str(e)}",
                deleted_count=0,
                deleted_size_bytes=0,
                deleted_size_mb=0
            )
    
    async def cleanup_orphaned_files(self) -> CleanupResult:
        """Clean up orphaned files that don't have database records"""
        try:
            logger.info("Starting cleanup of orphaned files")
            
            # Get all export file paths from database
            from app.core.firebase import db
            
            exports = db.collection("exports").stream()
            bulk_exports = db.collection("bulk_exports").stream()
            
            db_file_paths = set()
            for export_doc in exports:
                export_data = export_doc.to_dict()
                if export_data.get("file_path"):
                    db_file_paths.add(export_data["file_path"])
            
            for bulk_export_doc in bulk_exports:
                bulk_export_data = bulk_export_doc.to_dict()
                if bulk_export_data.get("zip_path"):
                    db_file_paths.add(bulk_export_data["zip_path"])
            
            # Scan export directories for orphaned files
            import os
            from pathlib import Path
            
            export_base = Path(self.config.EXPORT_BASE_PATH)
            if not export_base.exists():
                return CleanupResult(
                    message="Export base directory does not exist",
                    deleted_count=0,
                    deleted_size_bytes=0,
                    deleted_size_mb=0
                )
            
            orphaned_files = []
            for file_path in export_base.rglob('*'):
                if file_path.is_file():
                    if str(file_path) not in db_file_paths:
                        # Check if file is old enough (older than 2 days)
                        file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_age.days >= 2:
                            orphaned_files.append(str(file_path))
            
            # Clean up orphaned files
            files_deleted, bytes_freed = file_manager.cleanup_expired_files(orphaned_files)
            
            result = CleanupResult(
                message=f"Cleaned up {files_deleted} orphaned files",
                deleted_count=files_deleted,
                deleted_size_bytes=bytes_freed,
                deleted_size_mb=round(bytes_freed / (1024 * 1024), 2)
            )
            
            logger.info(f"Orphaned file cleanup completed: {result.message}")
            return result
            
        except Exception as e:
            logger.error(f"Error during orphaned file cleanup: {e}")
            return CleanupResult(
                message=f"Orphaned file cleanup failed: {str(e)}",
                deleted_count=0,
                deleted_size_bytes=0,
                deleted_size_mb=0
            )
    
    async def cleanup_old_usage_records(self) -> CleanupResult:
        """Clean up old usage tracking records (older than 1 year)"""
        try:
            logger.info("Starting cleanup of old usage records")
            
            from app.core.firebase import db
            
            # Delete usage records older than 1 year
            cutoff_date = datetime.now() - timedelta(days=365)
            old_usage_records = db.collection("export_usage").where(
                "month", "<", cutoff_date
            ).limit(self.config.CLEANUP_BATCH_SIZE).stream()
            
            deleted_count = 0
            for usage_doc in old_usage_records:
                try:
                    usage_doc.reference.delete()
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete usage record: {e}")
            
            result = CleanupResult(
                message=f"Cleaned up {deleted_count} old usage records",
                deleted_count=deleted_count,
                deleted_size_bytes=0,
                deleted_size_mb=0
            )
            
            logger.info(f"Usage record cleanup completed: {result.message}")
            return result
            
        except Exception as e:
            logger.error(f"Error during usage record cleanup: {e}")
            return CleanupResult(
                message=f"Usage record cleanup failed: {str(e)}",
                deleted_count=0,
                deleted_size_bytes=0,
                deleted_size_mb=0
            )
    
    async def cleanup_user_data(self, user_id: str) -> CleanupResult:
        """Clean up all export data for a specific user (GDPR compliance)"""
        try:
            logger.info(f"Starting cleanup of all data for user {user_id}")
            
            from app.core.firebase import db
            
            total_deleted = 0
            total_bytes_freed = 0
            
            # Clean up regular exports
            user_exports = db.collection("exports").where("user_id", "==", user_id).stream()
            export_files = []
            export_ids = []
            
            for export_doc in user_exports:
                export_data = export_doc.to_dict()
                if export_data.get("file_path"):
                    export_files.append(export_data["file_path"])
                export_ids.append(export_data["id"])
            
            # Clean up bulk exports
            user_bulk_exports = db.collection("bulk_exports").where("user_id", "==", user_id).stream()
            bulk_files = []
            bulk_ids = []
            
            for bulk_export_doc in user_bulk_exports:
                bulk_export_data = bulk_export_doc.to_dict()
                if bulk_export_data.get("zip_path"):
                    bulk_files.append(bulk_export_data["zip_path"])
                bulk_ids.append(bulk_export_data["id"])
            
            # Delete files
            all_files = export_files + bulk_files
            files_deleted, bytes_freed = file_manager.cleanup_expired_files(all_files)
            total_deleted += files_deleted
            total_bytes_freed += bytes_freed
            
            # Delete database records
            for export_id in export_ids:
                try:
                    db.collection("exports").document(export_id).delete()
                except Exception as e:
                    logger.warning(f"Failed to delete export record {export_id}: {e}")
            
            for bulk_id in bulk_ids:
                try:
                    db.collection("bulk_exports").document(bulk_id).delete()
                except Exception as e:
                    logger.warning(f"Failed to delete bulk export record {bulk_id}: {e}")
            
            # Clean up usage records
            usage_records = db.collection("export_usage").where("user_id", "==", user_id).stream()
            for usage_doc in usage_records:
                try:
                    usage_doc.reference.delete()
                except Exception as e:
                    logger.warning(f"Failed to delete usage record: {e}")
            
            # Clean up user directory
            user_files_deleted, user_bytes_freed = file_manager.cleanup_user_directory(user_id)
            total_deleted += user_files_deleted
            total_bytes_freed += user_bytes_freed
            
            result = CleanupResult(
                message=f"Cleaned up all export data for user {user_id}",
                deleted_count=total_deleted,
                deleted_size_bytes=total_bytes_freed,
                deleted_size_mb=round(total_bytes_freed / (1024 * 1024), 2)
            )
            
            logger.info(f"User data cleanup completed: {result.message}")
            return result
            
        except Exception as e:
            logger.error(f"Error during user data cleanup for {user_id}: {e}")
            return CleanupResult(
                message=f"User data cleanup failed: {str(e)}",
                deleted_count=0,
                deleted_size_bytes=0,
                deleted_size_mb=0
            )
    
    async def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get statistics about cleanup operations"""
        try:
            from app.core.firebase import db
            
            current_time = datetime.now()
            
            # Count expired exports
            expired_exports = db.collection("exports").where(
                "expires_at", "<", current_time
            ).stream()
            expired_count = sum(1 for _ in expired_exports)
            
            # Count expired bulk exports
            expired_bulk_exports = db.collection("bulk_exports").where(
                "expires_at", "<", current_time
            ).stream()
            expired_bulk_count = sum(1 for _ in expired_bulk_exports)
            
            # Count failed exports
            failed_exports = db.collection("exports").where(
                "status", "==", "failed"
            ).stream()
            failed_count = sum(1 for _ in failed_exports)
            
            # Calculate disk usage
            disk_usage = file_manager.get_directory_size(self.config.EXPORT_BASE_PATH)
            
            return {
                "expired_exports": expired_count,
                "expired_bulk_exports": expired_bulk_count,
                "failed_exports": failed_count,
                "total_disk_usage_bytes": disk_usage,
                "total_disk_usage_mb": round(disk_usage / (1024 * 1024), 2),
                "cleanup_enabled": self.config.AUTO_CLEANUP_ENABLED,
                "last_check": current_time
            }
            
        except Exception as e:
            logger.error(f"Error getting cleanup stats: {e}")
            return {
                "error": str(e),
                "last_check": current_time
            }

# Global cleanup service instance
cleanup_service = CleanupService()

# Auto-start cleanup if enabled
if export_config.AUTO_CLEANUP_ENABLED:
    cleanup_service.start_scheduler()