# app/services/subscription_service.py
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from app.core.firebase import db
from app.models.resume import SubscriptionInfo, SubscriptionPlan, ExportLimitCheck
from app.core.export_config import export_config
from app.exceptions.export_exceptions import ExportLimitExceededException

logger = logging.getLogger(__name__)

class SubscriptionService:
    """Handles subscription-related operations for exports"""
    
    def __init__(self):
        self.config = export_config
    
    async def get_user_subscription(self, user_id: str) -> SubscriptionInfo:
        """Get user subscription status and details"""
        try:
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return SubscriptionInfo(
                    is_subscribed=False,
                    plan=SubscriptionPlan.FREE
                )
            
            user_data = user_doc.to_dict()
            subscription_data = user_data.get("subscription", {})
            
            is_active = subscription_data.get("active", False)
            plan_name = subscription_data.get("plan", "free")
            
            # Map plan names to enum
            plan_mapping = {
                "free": SubscriptionPlan.FREE,
                "premium": SubscriptionPlan.PREMIUM,
                "enterprise": SubscriptionPlan.ENTERPRISE
            }
            
            plan = plan_mapping.get(plan_name.lower(), SubscriptionPlan.FREE)
            
            # Check if subscription is expired
            expires_at = subscription_data.get("expires_at")
            if expires_at and isinstance(expires_at, datetime) and expires_at < datetime.now():
                is_active = False
                plan = SubscriptionPlan.FREE
            
            return SubscriptionInfo(
                is_subscribed=is_active and plan != SubscriptionPlan.FREE,
                plan=plan,
                expires_at=expires_at,
                features=subscription_data.get("features", [])
            )
            
        except Exception as e:
            logger.error(f"Error getting subscription status for user {user_id}: {e}")
            return SubscriptionInfo(
                is_subscribed=False,
                plan=SubscriptionPlan.FREE
            )
    
    async def check_export_limits(self, user_id: str, subscription: SubscriptionInfo) -> ExportLimitCheck:
        """Check if user can export based on subscription and usage limits"""
        
        # Get subscription limits
        limits = self.config.subscription_limits.get(subscription.plan)
        if not limits:
            return ExportLimitCheck(
                can_export=False,
                reason="invalid_subscription",
            )
        
        # Unlimited exports for certain plans
        if limits.monthly_exports == -1:
            return ExportLimitCheck(
                can_export=True,
                reason="unlimited",
            )
        
        # Count recent exports for limited plans
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        try:
            recent_exports = db.collection("exports").where(
                "user_id", "==", user_id
            ).where(
                "created_at", ">=", thirty_days_ago
            ).where(
                "status", "==", "completed"
            ).stream()
            
            export_count = sum(1 for _ in recent_exports)
            
            if export_count >= limits.monthly_exports:
                return ExportLimitCheck(
                    can_export=False,
                    reason="limit_reached",
                    limit=limits.monthly_exports,
                    used=export_count,
                    remaining=0
                )
            
            return ExportLimitCheck(
                can_export=True,
                reason="within_limit",
                limit=limits.monthly_exports,
                used=export_count,
                remaining=limits.monthly_exports - export_count
            )
            
        except Exception as e:
            logger.error(f"Error checking export limits for user {user_id}: {e}")
            # Fail safely - allow export but log error
            return ExportLimitCheck(
                can_export=True,
                reason="check_failed",
            )
    
    async def validate_bulk_export_permission(self, user_id: str, resume_count: int) -> bool:
        """Validate if user can perform bulk export"""
        subscription = await self.get_user_subscription(user_id)
        limits = self.config.subscription_limits.get(subscription.plan)
        
        if not limits or not limits.bulk_export_enabled:
            return False
        
        if resume_count > limits.max_bulk_resumes:
            return False
        
        return True
    
    async def is_admin_user(self, user_id: str) -> bool:
        """Check if user has admin privileges"""
        try:
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return False
            
            user_data = user_doc.to_dict()
            return user_data.get("is_admin", False)
            
        except Exception as e:
            logger.error(f"Error checking admin status for user {user_id}: {e}")
            return False
    
    async def increment_export_usage(self, user_id: str) -> None:
        """Increment user's export usage counter"""
        try:
            current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            usage_ref = db.collection("export_usage").document(f"{user_id}_{current_month.strftime('%Y%m')}")
            usage_doc = usage_ref.get()
            
            if usage_doc.exists:
                usage_data = usage_doc.to_dict()
                current_count = usage_data.get("count", 0)
                usage_ref.update({
                    "count": current_count + 1,
                    "last_export": datetime.now()
                })
            else:
                usage_ref.set({
                    "user_id": user_id,
                    "month": current_month,
                    "count": 1,
                    "first_export": datetime.now(),
                    "last_export": datetime.now()
                })
                
        except Exception as e:
            logger.error(f"Error incrementing export usage for user {user_id}: {e}")
    
    async def get_monthly_usage(self, user_id: str) -> int:
        """Get user's current monthly export usage"""
        try:
            current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            usage_ref = db.collection("export_usage").document(f"{user_id}_{current_month.strftime('%Y%m')}")
            usage_doc = usage_ref.get()
            
            if usage_doc.exists:
                usage_data = usage_doc.to_dict()
                return usage_data.get("count", 0)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error getting monthly usage for user {user_id}: {e}")
            return 0
    
    def get_plan_features(self, plan: SubscriptionPlan) -> Dict[str, Any]:
        """Get features available for a subscription plan"""
        limits = self.config.subscription_limits.get(plan)
        
        if not limits:
            return {}
        
        return {
            "monthly_exports": limits.monthly_exports if limits.monthly_exports != -1 else "unlimited",
            "max_file_size_mb": limits.file_size_mb,
            "export_expiry_hours": limits.export_expiry_hours,
            "bulk_export": limits.bulk_export_enabled,
            "max_bulk_resumes": limits.max_bulk_resumes if limits.bulk_export_enabled else 0,
            "priority_support": plan in [SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE],
            "advanced_templates": plan in [SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE],
            "api_access": plan == SubscriptionPlan.ENTERPRISE
        }

# Global subscription service instance
subscription_service = SubscriptionService()