# app/services/file_manager.py
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Tuple
import logging
from contextlib import contextmanager

from app.core.export_config import export_config
from app.exceptions.export_exceptions import FileSystemException

logger = logging.getLogger(__name__)

class FileManager:
    """Handles file operations for exports with security and cleanup"""
    
    def __init__(self):
        self.base_path = Path(export_config.EXPORT_BASE_PATH)
        self.temp_path = Path(export_config.TEMP_EXPORT_PATH)
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            self.temp_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileSystemException("create_directory", str(self.base_path), str(e))
    
    def _sanitize_path_component(self, component: str) -> str:
        """Sanitize a path component to prevent directory traversal"""
        # Remove any path traversal attempts
        sanitized = component.replace('..', '').replace('/', '').replace('\\', '')
        # Keep only alphanumeric, hyphens, underscores, and periods
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '-_.')
        # Limit length
        return sanitized[:50] if sanitized else str(uuid.uuid4())[:8]
    
    def generate_export_path(self, user_id: str, resume_id: str, format_type: str) -> str:
        """Generate a secure file path for export"""
        safe_user_id = self._sanitize_path_component(user_id)
        safe_resume_id = self._sanitize_path_component(resume_id)
        timestamp = str(int(os.time.time()))
        filename = f"{safe_resume_id}_{timestamp}.{format_type.lower()}"
        
        user_dir = self.base_path / safe_user_id
        user_dir.mkdir(exist_ok=True)
        
        return str(user_dir / filename)
    
    def generate_bulk_export_path(self, user_id: str, format_type: str) -> str:
        """Generate a secure path for bulk export ZIP"""
        safe_user_id = self._sanitize_path_component(user_id)
        timestamp = str(int(os.time.time()))
        filename = f"bulk_export_{timestamp}.zip"
        
        user_dir = self.base_path / safe_user_id
        user_dir.mkdir(exist_ok=True)
        
        return str(user_dir / filename)
    
    @contextmanager
    def temporary_file(self, suffix: str = ""):
        """Context manager for temporary files"""
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(
                dir=self.temp_path,
                suffix=suffix,
                delete=False
            )
            yield temp_file.name
        finally:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except OSError as e:
                    logger.warning(f"Failed to cleanup temp file {temp_file.name}: {e}")
    
    def move_file(self, source: str, destination: str) -> bool:
        """Safely move a file from source to destination"""
        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination)
            os.makedirs(dest_dir, exist_ok=True)
            
            shutil.move(source, destination)
            return True
        except (OSError, shutil.Error) as e:
            logger.error(f"Failed to move file from {source} to {destination}: {e}")
            raise FileSystemException("move_file", f"{source} -> {destination}", str(e))
    
    def copy_file(self, source: str, destination: str) -> bool:
        """Safely copy a file"""
        try:
            dest_dir = os.path.dirname(destination)
            os.makedirs(dest_dir, exist_ok=True)
            
            shutil.copy2(source, destination)
            return True
        except (OSError, shutil.Error) as e:
            logger.error(f"Failed to copy file from {source} to {destination}: {e}")
            raise FileSystemException("copy_file", f"{source} -> {destination}", str(e))
    
    def delete_file(self, file_path: str) -> bool:
        """Safely delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except OSError as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise FileSystemException("delete_file", file_path, str(e))
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return 0
        except OSError as e:
            logger.error(f"Failed to get size of file {file_path}: {e}")
            return 0
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    def cleanup_user_directory(self, user_id: str) -> Tuple[int, int]:
        """Clean up all files in a user's directory. Returns (files_deleted, bytes_freed)"""
        safe_user_id = self._sanitize_path_component(user_id)
        user_dir = self.base_path / safe_user_id
        
        if not user_dir.exists():
            return 0, 0
        
        files_deleted = 0
        bytes_freed = 0
        
        try:
            for file_path in user_dir.rglob('*'):
                if file_path.is_file():
                    try:
                        size = file_path.stat().st_size
                        file_path.unlink()
                        files_deleted += 1
                        bytes_freed += size
                    except OSError as e:
                        logger.warning(f"Failed to delete {file_path}: {e}")
            
            # Try to remove empty directories
            try:
                user_dir.rmdir()
            except OSError:
                pass  # Directory not empty or other error
                
        except OSError as e:
            logger.error(f"Error during cleanup of user directory {user_dir}: {e}")
        
        return files_deleted, bytes_freed
    
    def cleanup_expired_files(self, file_paths: list) -> Tuple[int, int]:
        """Clean up a list of expired files. Returns (files_deleted, bytes_freed)"""
        files_deleted = 0
        bytes_freed = 0
        
        for file_path in file_paths:
            try:
                if self.file_exists(file_path):
                    size = self.get_file_size(file_path)
                    self.delete_file(file_path)
                    files_deleted += 1
                    bytes_freed += size
            except Exception as e:
                logger.warning(f"Failed to cleanup expired file {file_path}: {e}")
        
        return files_deleted, bytes_freed
    
    def validate_file_size(self, file_path: str, max_size_mb: int) -> bool:
        """Validate file size against maximum allowed"""
        if not self.file_exists(file_path):
            return False
        
        file_size = self.get_file_size(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        return file_size <= max_size_bytes
    
    def get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        continue
        except OSError as e:
            logger.error(f"Error calculating directory size for {directory}: {e}")
        
        return total_size

# Global file manager instance
file_manager = FileManager()