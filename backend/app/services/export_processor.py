# app/services/export_processor.py
import asyncio
import zipfile
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import os

from app.models.resume import ExportFormat, ExportStatus, SubscriptionPlan
from app.services.file_manager import file_manager
from app.services.export_database_service import export_db_service
from app.services.export_service import export_to_pdf, export_to_docx
from app.core.export_config import export_config
from app.exceptions.export_exceptions import (
    ExportProcessingException, FileSizeExceededException, FileSystemException
)

logger = logging.getLogger(__name__)

class ExportProcessor:
    """Handles the actual export processing with retry logic and error handling"""
    
    def __init__(self):
        self.config = export_config
        self.max_retries = self.config.MAX_EXPORT_RETRIES
        self.retry_delay = self.config.RETRY_DELAY_SECONDS
    
    async def process_single_export(
        self,
        export_id: str,
        resume_data: Dict[str, Any],
        content: Dict[str, Any],
        file_path: str,
        format_type: ExportFormat
    ) -> bool:
        """Process a single export with retry logic"""
        
        for attempt in range(self.max_retries + 1):
            try:
                await export_db_service.update_export_status(export_id, ExportStatus.PROCESSING)
                
                # Call appropriate export service
                if format_type == ExportFormat.PDF:
                    success = await self._export_pdf_with_validation(
                        resume_data, content, file_path, export_id
                    )
                elif format_type == ExportFormat.DOCX:
                    success = await self._export_docx_with_validation(
                        resume_data, content, file_path, export_id
                    )
                else:
                    logger.error(f"Unknown export format: {format_type}")
                    await export_db_service.update_export_status(
                        export_id, ExportStatus.FAILED, 
                        error_message="Unknown export format"
                    )
                    return False
                
                if success:
                    logger.info(f"Export {export_id} completed successfully")
                    return True
                else:
                    raise ExportProcessingException(export_id, "Export generation returned False")
                
            except FileSizeExceededException as e:
                # Don't retry for size limit errors
                logger.error(f"Export {export_id} failed due to size limit: {e}")
                await export_db_service.update_export_status(
                    export_id, ExportStatus.FAILED, 
                    error_message="File size exceeds limit"
                )
                
                # Clean up file if it exists
                if file_manager.file_exists(file_path):
                    file_manager.delete_file(file_path)
                
                return False
                
            except Exception as e:
                logger.error(f"Export {export_id} attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries:
                    # Final attempt failed
                    await export_db_service.update_export_status(
                        export_id, ExportStatus.FAILED, 
                        error_message=str(e)
                    )
                    return False
                else:
                    # Wait before retry
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        return False
    
    async def _export_pdf_with_validation(
        self, 
        resume_data: Dict[str, Any], 
        content: Dict[str, Any], 
        file_path: str,
        export_id: str
    ) -> bool:
        """Export to PDF with validation"""
        
        # Use temporary file first
        with file_manager.temporary_file(suffix=".pdf") as temp_path:
            success = await export_to_pdf(resume_data, content, temp_path)
            
            if not success or not file_manager.file_exists(temp_path):
                return False
            
            # Validate file size
            file_size = file_manager.get_file_size(temp_path)
            max_size_mb = self.config.MAX_EXPORT_SIZE_MB
            
            if not file_manager.validate_file_size(temp_path, max_size_mb):
                raise FileSizeExceededException(file_size, max_size_mb * 1024 * 1024)
            
            # Move to final location
            file_manager.move_file(temp_path, file_path)
            
            # Update database with file size
            await export_db_service.update_export_status(
                export_id, ExportStatus.COMPLETED, file_size
            )
            
            return True
    
    async def _export_docx_with_validation(
        self, 
        resume_data: Dict[str, Any], 
        content: Dict[str, Any], 
        file_path: str,
        export_id: str
    ) -> bool:
        """Export to DOCX with validation"""
        
        # Use temporary file first
        with file_manager.temporary_file(suffix=".docx") as temp_path:
            success = await export_to_docx(resume_data, content, temp_path)
            
            if not success or not file_manager.file_exists(temp_path):
                return False
            
            # Validate file size
            file_size = file_manager.get_file_size(temp_path)
            max_size_mb = self.config.MAX_EXPORT_SIZE_MB
            
            if not file_manager.validate_file_size(temp_path, max_size_mb):
                raise FileSizeExceededException(file_size, max_size_mb * 1024 * 1024)
            
            # Move to final location
            file_manager.move_file(temp_path, file_path)
            
            # Update database with file size
            await export_db_service.update_export_status(
                export_id, ExportStatus.COMPLETED, file_size
            )
            
            return True
    
    async def process_bulk_export(
        self,
        bulk_export_id: str,
        resumes: List[Dict[str, Any]],
        format_type: ExportFormat,
        zip_path: str
    ) -> bool:
        """Process bulk export with progress tracking"""
        
        try:
            await export_db_service.update_bulk_export_progress(
                bulk_export_id, ExportStatus.PROCESSING, 0
            )
            
            temp_files = []
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                total_resumes = len(resumes)
                
                for i, resume_data in enumerate(resumes):
                    try:
                        # Generate individual file
                        temp_filename = f"temp_{resume_data['id']}.{format_type.value}"
                        
                        with file_manager.temporary_file(suffix=f".{format_type.value}") as temp_path:
                            # Export individual resume
                            success = False
                            if format_type == ExportFormat.PDF:
                                success = await export_to_pdf(
                                    resume_data, 
                                    resume_data.get("ai_content", {}), 
                                    temp_path
                                )
                            elif format_type == ExportFormat.DOCX:
                                success = await export_to_docx(
                                    resume_data, 
                                    resume_data.get("ai_content", {}), 
                                    temp_path
                                )
                            
                            if success and file_manager.file_exists(temp_path):
                                # Generate safe filename for ZIP
                                safe_title = self._sanitize_resume_title(
                                    resume_data.get('title', 'resume')
                                )
                                zip_filename = f"{safe_title}.{format_type.value}"
                                
                                # Ensure unique filename in ZIP
                                counter = 1
                                original_filename = zip_filename
                                while zip_filename in [info.filename for info in zip_file.infolist()]:
                                    name, ext = os.path.splitext(original_filename)
                                    zip_filename = f"{name}_{counter}{ext}"
                                    counter += 1
                                
                                zip_file.write(temp_path, zip_filename)
                                
                                # Update progress
                                progress = int((i + 1) / total_resumes * 90)  # 90% for generation
                                await export_db_service.update_bulk_export_progress(
                                    bulk_export_id, ExportStatus.PROCESSING, progress
                                )
                                
                    except Exception as e:
                        logger.error(f"Error exporting resume {resume_data.get('id')} in bulk export: {e}")
                        continue
            
            # Validate ZIP file
            if not file_manager.file_exists(zip_path):
                raise FileSystemException("create_zip", zip_path, "ZIP file was not created")
            
            zip_size = file_manager.get_file_size(zip_path)
            if zip_size == 0:
                raise FileSystemException("create_zip", zip_path, "ZIP file is empty")
            
            # Validate ZIP size
            max_size_mb = self.config.MAX_BULK_EXPORT_SIZE_MB
            if not file_manager.validate_file_size(zip_path, max_size_mb):
                file_manager.delete_file(zip_path)
                raise FileSizeExceededException(zip_size, max_size_mb * 1024 * 1024)
            
            # Update to completed
            await export_db_service.update_bulk_export_progress(
                bulk_export_id, ExportStatus.COMPLETED, 100, zip_size
            )
            
            logger.info(f"Bulk export {bulk_export_id} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Bulk export {bulk_export_id} failed: {e}")
            await export_db_service.update_bulk_export_progress(
                bulk_export_id, ExportStatus.FAILED, 0, error_message=str(e)
            )
            
            # Clean up ZIP file if it exists
            if file_manager.file_exists(zip_path):
                file_manager.delete_file(zip_path)
            
            return False
    
    def _sanitize_resume_title(self, title: str) -> str:
        """Sanitize resume title for use in filenames"""
        # Remove or replace invalid characters
        safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_', '.'))
        # Replace spaces with underscores and limit length
        safe_title = safe_title.replace(' ', '_')[:50]
        return safe_title if safe_title else "resume"
    
    async def cleanup_failed_exports(self, max_age_hours: int = 24) -> int:
        """Clean up failed export files older than specified age"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            # Get failed exports older than cutoff
            failed_exports = await export_db_service.get_exports_by_status_and_age(
                ExportStatus.FAILED, cutoff_time
            )
            
            cleaned_count = 0
            for export_record in failed_exports:
                try:
                    if file_manager.file_exists(export_record.file_path):
                        file_manager.delete_file(export_record.file_path)
                    
                    await export_db_service.delete_export_record(export_record.id, export_record.user_id)
                    cleaned_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to cleanup export {export_record.id}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} failed exports")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during failed export cleanup: {e}")
            return 0

# Global export processor instance
export_processor = ExportProcessor()