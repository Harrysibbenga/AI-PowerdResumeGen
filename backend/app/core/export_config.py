# app/config/export_config.py
from dataclasses import dataclass
from typing import Dict
from app.models.resume import SubscriptionPlan, ExportLimits

@dataclass
class ExportConfig:
    """Export system configuration"""
    
    # File size limits (in MB)
    MAX_EXPORT_SIZE_MB: int = 50
    MAX_BULK_EXPORT_SIZE_MB: int = 200
    
    # Time limits
    EXPORT_EXPIRY_HOURS: int = 24
    BULK_EXPORT_EXPIRY_HOURS: int = 48
    
    # Rate limits
    FREE_EXPORTS_PER_MONTH: int = 3
    PREMIUM_EXPORTS_PER_MONTH: int = 100  # High limit, essentially unlimited
    
    # Bulk export limits
    MAX_BULK_RESUMES: int = 20
    BULK_EXPORT_TIMEOUT_MINUTES: int = 30
    
    # File paths
    EXPORT_BASE_PATH: str = "exports"
    TEMP_EXPORT_PATH: str = "temp_exports"
    
    # Retry configuration
    MAX_EXPORT_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 5
    
    # Cleanup configuration
    CLEANUP_BATCH_SIZE: int = 100
    AUTO_CLEANUP_ENABLED: bool = True
    
    @property
    def subscription_limits(self) -> Dict[SubscriptionPlan, ExportLimits]:
        """Get export limits by subscription plan"""
        return {
            SubscriptionPlan.FREE: ExportLimits(
                monthly_exports=self.FREE_EXPORTS_PER_MONTH,
                file_size_mb=self.MAX_EXPORT_SIZE_MB,
                export_expiry_hours=self.EXPORT_EXPIRY_HOURS,
                bulk_export_enabled=False,
                max_bulk_resumes=0
            ),
            SubscriptionPlan.PREMIUM: ExportLimits(
                monthly_exports=self.PREMIUM_EXPORTS_PER_MONTH,
                file_size_mb=self.MAX_EXPORT_SIZE_MB,
                export_expiry_hours=self.EXPORT_EXPIRY_HOURS,
                bulk_export_enabled=True,
                max_bulk_resumes=self.MAX_BULK_RESUMES
            ),
            SubscriptionPlan.ENTERPRISE: ExportLimits(
                monthly_exports=-1,  # Unlimited
                file_size_mb=self.MAX_BULK_EXPORT_SIZE_MB,
                export_expiry_hours=self.BULK_EXPORT_EXPIRY_HOURS,
                bulk_export_enabled=True,
                max_bulk_resumes=50
            )
        }

# Global config instance
export_config = ExportConfig()