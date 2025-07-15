# app/exceptions/export_exceptions.py
from typing import Optional

class ExportBaseException(Exception):
    """Base exception for export operations"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ExportLimitExceededException(ExportBaseException):
    """Raised when export limit is exceeded"""
    
    def __init__(self, limit: int, used: int, plan: str):
        self.limit = limit
        self.used = used
        self.plan = plan
        message = f"Export limit exceeded. Used {used}/{limit} exports for {plan} plan"
        super().__init__(message, "EXPORT_LIMIT_EXCEEDED")

class ExportNotFoundException(ExportBaseException):
    """Raised when export is not found"""
    
    def __init__(self, export_id: str):
        self.export_id = export_id
        message = f"Export with ID {export_id} not found"
        super().__init__(message, "EXPORT_NOT_FOUND")

class ExportExpiredException(ExportBaseException):
    """Raised when export has expired"""
    
    def __init__(self, export_id: str):
        self.export_id = export_id
        message = f"Export {export_id} has expired"
        super().__init__(message, "EXPORT_EXPIRED")

class ExportProcessingException(ExportBaseException):
    """Raised when export is still processing"""
    
    def __init__(self, export_id: str):
        self.export_id = export_id
        message = f"Export {export_id} is still processing"
        super().__init__(message, "EXPORT_PROCESSING")

class ExportFailedException(ExportBaseException):
    """Raised when export has failed"""
    
    def __init__(self, export_id: str, error_message: Optional[str] = None):
        self.export_id = export_id
        self.error_message = error_message
        message = f"Export {export_id} failed"
        if error_message:
            message += f": {error_message}"
        super().__init__(message, "EXPORT_FAILED")

class UnauthorizedExportAccessException(ExportBaseException):
    """Raised when user tries to access export they don't own"""
    
    def __init__(self, export_id: str, user_id: str):
        self.export_id = export_id
        self.user_id = user_id
        message = f"User {user_id} is not authorized to access export {export_id}"
        super().__init__(message, "UNAUTHORIZED_EXPORT_ACCESS")

class InvalidExportFormatException(ExportBaseException):
    """Raised when invalid export format is specified"""
    
    def __init__(self, format_type: str):
        self.format_type = format_type
        message = f"Invalid export format: {format_type}"
        super().__init__(message, "INVALID_EXPORT_FORMAT")

class FileSizeExceededException(ExportBaseException):
    """Raised when file size exceeds limits"""
    
    def __init__(self, file_size: int, max_size: int):
        self.file_size = file_size
        self.max_size = max_size
        message = f"File size {file_size} bytes exceeds maximum {max_size} bytes"
        super().__init__(message, "FILE_SIZE_EXCEEDED")

class BulkExportLimitException(ExportBaseException):
    """Raised when bulk export limits are exceeded"""
    
    def __init__(self, requested: int, max_allowed: int):
        self.requested = requested
        self.max_allowed = max_allowed
        message = f"Requested {requested} resumes exceeds maximum {max_allowed} for bulk export"
        super().__init__(message, "BULK_EXPORT_LIMIT_EXCEEDED")

class PremiumFeatureRequiredException(ExportBaseException):
    """Raised when premium feature is required"""
    
    def __init__(self, feature: str):
        self.feature = feature
        message = f"{feature} is a premium feature. Please upgrade your subscription."
        super().__init__(message, "PREMIUM_FEATURE_REQUIRED")

class ResumeNotFoundException(ExportBaseException):
    """Raised when resume is not found"""
    
    def __init__(self, resume_id: str):
        self.resume_id = resume_id
        message = f"Resume with ID {resume_id} not found"
        super().__init__(message, "RESUME_NOT_FOUND")

class ResumeDeletedExceptionException(ExportBaseException):
    """Raised when resume has been deleted"""
    
    def __init__(self, resume_id: str):
        self.resume_id = resume_id
        message = f"Resume {resume_id} has been deleted"
        super().__init__(message, "RESUME_DELETED")

class FileSystemException(ExportBaseException):
    """Raised when file system operations fail"""
    
    def __init__(self, operation: str, path: str, error: str):
        self.operation = operation
        self.path = path
        self.error = error
        message = f"File system error during {operation} on {path}: {error}"
        super().__init__(message, "FILE_SYSTEM_ERROR")