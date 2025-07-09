"""
Authentication router
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict
from datetime import datetime, timedelta

# Import our separated modules
from app.models.auth_models import (
    UserCreate, UserResponse, ForgotPasswordRequest, ResetPasswordRequest,
    VerifyEmailRequest, Setup2FAResponse, Verify2FARequest, Enable2FARequest,
    SessionResponse, MessageResponse, UserDocument
)
from app.helpers.auth_helpers import AuthHelpers, ValidationHelpers
from app.services.email_service import email_service
from app.services.two_factor_service import two_factor_service
from app.dependencies.auth_dependencies import (
    get_current_user, get_verified_user, rate_limit_auth, 
    rate_limit_email, rate_limit_2fa
)

# Import Firebase from your existing setup
from app.core.firebase import db, firebase_auth, check_firebase_health
from firebase_admin import auth, firestore

from app.core.config import settings

router = APIRouter()

# =============================================================================
# USER MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/users", response_model=UserResponse, dependencies=[Depends(rate_limit_auth)])
async def create_user(user_data: UserCreate, background_tasks: BackgroundTasks):
    """Create a new user with email verification"""
    try:
        # Validate password strength
        password_validation = ValidationHelpers.validate_password_strength(user_data.password)
        if not password_validation["is_strong"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet requirements",
                    "suggestions": password_validation["suggestions"]
                }
            )
        
        # Sanitize display name
        display_name = ValidationHelpers.sanitize_display_name(user_data.displayName or "")
        
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=display_name,
            email_verified=False
        )
        
        # Generate email verification token
        verification_token = AuthHelpers.generate_secure_token()
        
        # Create user document
        user_doc = UserDocument(
            uid=user.uid,
            email=user.email,
            display_name=display_name,
            email_verification_token=verification_token,
            email_verification_expires=AuthHelpers.create_expiration_time(24)
        )
        
        await AuthHelpers.create_user_document(user_doc)
        
        # Send verification email
        background_tasks.add_task(
            email_service.send_verification_email,
            user.email,
            display_name,
            verification_token
        )
        
        return UserResponse(
            uid=user.uid,
            email=user.email,
            displayName=display_name,
            isSubscribed=False,
            emailVerified=False,
            twoFactorEnabled=False
        )
    
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {str(e)}"
        )

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(user_data: Dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        user_id = user_data["uid"]
        user_doc = await AuthHelpers.get_user_document(user_id)
        
        if not user_doc:
            # Create missing user document
            firebase_user = auth.get_user(user_id)
            user_document = UserDocument(
                uid=firebase_user.uid,
                email=firebase_user.email,
                display_name=firebase_user.display_name or "",
                email_verified=firebase_user.email_verified
            )
            await AuthHelpers.create_user_document(user_document)
            user_doc = user_document.dict()
        
        return UserResponse(
            uid=user_doc["uid"],
            email=user_doc["email"],
            displayName=user_doc.get("display_name", ""),
            isSubscribed=user_doc.get("subscription", False),
            emailVerified=user_doc.get("email_verified", False),
            twoFactorEnabled=user_doc.get("two_factor_enabled", False)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profile: {str(e)}"
        )

@router.delete("/users/me", response_model=MessageResponse)
async def delete_user(user_data: Dict = Depends(get_current_user)):
    """Delete current user account"""
    try:
        user_id = user_data["uid"]
        
        # Delete user from Firebase Authentication
        auth.delete_user(user_id)
        
        # Delete user document from Firestore
        await AuthHelpers.delete_user_document(user_id)
        
        return MessageResponse(message="User deleted successfully")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )

# =============================================================================
# PASSWORD RESET ENDPOINTS
# =============================================================================

@router.post("/forgot-password", response_model=MessageResponse, dependencies=[Depends(rate_limit_email)])
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    """Send password reset email"""
    try:
        # Check if user exists (don't reveal if email exists for security)
        try:
            user = auth.get_user_by_email(request.email)
        except auth.UserNotFoundError:
            return MessageResponse(message="If the email exists, a password reset link has been sent.")
        
        # Generate reset token
        reset_token = AuthHelpers.generate_secure_token()
        
        # Update user document with reset token
        await AuthHelpers.update_user_document(user.uid, {
            "password_reset_token": reset_token,
            "password_reset_expires": AuthHelpers.create_expiration_time(1)
        })
        
        # Get user document for display name
        user_doc = await AuthHelpers.get_user_document(user.uid)
        display_name = user_doc.get("display_name", "") if user_doc else ""
        
        # Send reset email
        background_tasks.add_task(
            email_service.send_password_reset_email,
            request.email,
            display_name,
            reset_token
        )
        
        return MessageResponse(message="If the email exists, a password reset link has been sent.")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing password reset: {str(e)}"
        )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest, background_tasks: BackgroundTasks):
    """Reset password using reset token"""
    try:
        # Validate new password strength
        password_validation = ValidationHelpers.validate_password_strength(request.newPassword)
        if not password_validation["is_strong"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet requirements",
                    "suggestions": password_validation["suggestions"]
                }
            )
        
        # Find user by reset token
        user_info = await AuthHelpers.find_user_by_token("password_reset_token", request.token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        user_data = user_info["data"]
        user_ref = user_info["reference"]
        
        # Check if token is expired
        if AuthHelpers.is_expired(user_data["password_reset_expires"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        # Update password in Firebase Auth
        auth.update_user(user_data["uid"], password=request.newPassword)
        
        # Clear reset token and send notification
        user_ref.update({
            "password_reset_token": firestore.DELETE_FIELD,
            "password_reset_expires": firestore.DELETE_FIELD
        })
        
        # Send password change notification
        background_tasks.add_task(
            email_service.send_password_changed_notification,
            user_data["email"],
            user_data.get("display_name", "")
        )
        
        return MessageResponse(message="Password updated successfully")
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting password: {str(e)}"
        )

# =============================================================================
# EMAIL VERIFICATION ENDPOINTS
# =============================================================================

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(request: VerifyEmailRequest, background_tasks: BackgroundTasks):
    """Verify email address using verification token"""
    try:
        # Find user by verification token
        user_info = await AuthHelpers.find_user_by_token("email_verification_token", request.token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        user_data = user_info["data"]
        user_ref = user_info["reference"]
        
        # Check if token is expired
        if AuthHelpers.is_expired(user_data["email_verification_expires"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired"
            )
        
        # Update email verification status
        auth.update_user(user_data["uid"], email_verified=True)
        
        user_ref.update({
            "email_verified": True,
            "email_verification_token": firestore.DELETE_FIELD,
            "email_verification_expires": firestore.DELETE_FIELD
        })
        
        # Send welcome email
        background_tasks.add_task(
            email_service.send_welcome_email,
            user_data["email"],
            user_data.get("display_name", "")
        )
        
        return MessageResponse(message="Email verified successfully")
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying email: {str(e)}"
        )

@router.post("/resend-verification", response_model=MessageResponse, dependencies=[Depends(rate_limit_email)])
async def resend_verification_email(
    user_data: Dict = Depends(get_current_user), 
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Resend email verification"""
    try:
        user_id = user_data["uid"]
        user_doc = await AuthHelpers.get_user_document(user_id)
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user_doc.get("email_verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Generate new verification token
        verification_token = AuthHelpers.generate_secure_token()
        
        await AuthHelpers.update_user_document(user_id, {
            "email_verification_token": verification_token,
            "email_verification_expires": AuthHelpers.create_expiration_time(24)
        })
        
        # Send verification email
        background_tasks.add_task(
            email_service.send_verification_email,
            user_doc["email"],
            user_doc.get("display_name", ""),
            verification_token
        )
        
        return MessageResponse(message="Verification email sent successfully")
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending verification email: {str(e)}"
        )

# =============================================================================
# TWO-FACTOR AUTHENTICATION ENDPOINTS
# =============================================================================

@router.post("/2fa/setup", response_model=Setup2FAResponse, dependencies=[Depends(rate_limit_2fa)])
async def setup_2fa(user_data: Dict = Depends(get_verified_user)):
    """Setup two-factor authentication"""
    try:
        user_id = user_data["uid"]
        email = user_data["email"]
        
        # Generate secret for TOTP
        secret = two_factor_service.generate_secret()
        
        # Store temporary secret in Firestore
        await AuthHelpers.update_user_document(user_id, {
            "two_factor_secret_temp": secret
        })
        
        # Generate QR code and manual entry key
        qr_data = two_factor_service.generate_qr_code(secret, email)
        
        return Setup2FAResponse(
            qr_code=qr_data["qr_code"],
            secret=qr_data["manual_entry_key"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting up 2FA: {str(e)}"
        )

@router.post("/2fa/enable", response_model=MessageResponse)
async def enable_2fa(
    request: Enable2FARequest, 
    user_data: Dict = Depends(get_verified_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Enable two-factor authentication"""
    try:
        user_id = user_data["uid"]
        user_doc = await AuthHelpers.get_user_document(user_id)
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        secret = user_doc.get("two_factor_secret_temp")
        if not secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA setup not initiated. Please run setup first."
            )
        
        # Verify the code
        if not two_factor_service.verify_code(secret, request.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code"
            )
        
        # Enable 2FA
        await AuthHelpers.update_user_document(user_id, {
            "two_factor_enabled": True,
            "two_factor_secret": secret,
            "two_factor_secret_temp": firestore.DELETE_FIELD
        })
        
        # Send notification email
        background_tasks.add_task(
            email_service.send_2fa_enabled_notification,
            user_doc["email"],
            user_doc.get("display_name", "")
        )
        
        return MessageResponse(message="2FA enabled successfully")
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enabling 2FA: {str(e)}"
        )

@router.post("/2fa/disable", response_model=MessageResponse)
async def disable_2fa(
    request: Verify2FARequest, 
    user_data: Dict = Depends(get_verified_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Disable two-factor authentication"""
    try:
        user_id = user_data["uid"]
        user_doc = await AuthHelpers.get_user_document(user_id)
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user_doc.get("two_factor_enabled", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is not enabled"
            )
        
        secret = user_doc.get("two_factor_secret")
        if not two_factor_service.verify_code(secret, request.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code"
            )
        
        # Disable 2FA
        await AuthHelpers.update_user_document(user_id, {
            "two_factor_enabled": False,
            "two_factor_secret": firestore.DELETE_FIELD
        })
        
        # Send notification email
        background_tasks.add_task(
            email_service.send_2fa_disabled_notification,
            user_doc["email"],
            user_doc.get("display_name", "")
        )
        
        return MessageResponse(message="2FA disabled successfully")
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disabling 2FA: {str(e)}"
        )

@router.post("/2fa/verify", response_model=MessageResponse)
async def verify_2fa(request: Verify2FARequest, user_data: Dict = Depends(get_current_user)):
    """Verify 2FA code"""
    try:
        user_id = user_data["uid"]
        user_doc = await AuthHelpers.get_user_document(user_id)
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user_doc.get("two_factor_enabled", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is not enabled for this user"
            )
        
        secret = user_doc.get("two_factor_secret")
        if not two_factor_service.verify_code(secret, request.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code"
            )
        
        return MessageResponse(message="2FA code verified successfully")
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying 2FA: {str(e)}"
        )

# =============================================================================
# SESSION MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/logout", response_model=MessageResponse)
async def logout(user_data: Dict = Depends(get_current_user)):
    """Logout user by invalidating session"""
    try:
        user_id = user_data["uid"]
        
        # Force session expiration by updating last activity to past
        await AuthHelpers.update_user_document(user_id, {
            "last_activity": datetime.now() - timedelta(hours=25)
        })
        
        return MessageResponse(message="Logged out successfully")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging out: {str(e)}"
        )

@router.get("/session/status", response_model=SessionResponse)
async def get_session_status(user_data: Dict = Depends(get_current_user)):
    """Get current session status"""
    try:
        user_id = user_data["uid"]
        
        session_info = await AuthHelpers.check_session_validity(user_id, settings.SESSION_TIMEOUT_HOURS)
        
        return SessionResponse(
            sessionId=user_id,
            expiresAt=session_info.get("expires_at"),
            isValid=session_info["valid"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking session status: {str(e)}"
        )

@router.post("/session/extend", response_model=MessageResponse)
async def extend_session(user_data: Dict = Depends(get_current_user)):
    """Extend current session"""
    try:
        user_id = user_data["uid"]
        
        # Update last activity to extend session
        await AuthHelpers.update_last_activity(user_id)
        
        new_expires_at = datetime.now() + timedelta(hours=settings.SESSION_TIMEOUT_HOURS)
        
        return MessageResponse(message=f"Session extended until {new_expires_at.isoformat()}")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extending session: {str(e)}"
        )

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.post("/cleanup-tokens", response_model=MessageResponse)
async def cleanup_expired_tokens():
    """Cleanup expired tokens (admin endpoint)"""
    try:
        cleaned_count = await AuthHelpers.cleanup_expired_tokens()
        return MessageResponse(message=f"Cleaned up {cleaned_count} expired tokens")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleaning up tokens: {str(e)}"
        )

@router.get("/health", response_model=MessageResponse)
async def health_check():
    """Health check endpoint"""
    return MessageResponse(message="Authentication service is healthy")

# =============================================================================
# ADDITIONAL CONVENIENCE ENDPOINTS
# =============================================================================

@router.get("/user/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, current_user: Dict = Depends(get_current_user)):
    """Get user by ID (admin only or same user)"""
    try:
        # Check if requesting own profile or admin
        if current_user["uid"] != user_id:
            # Check admin permissions (would need to implement admin check)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        user_doc = await AuthHelpers.get_user_document(user_id)
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            uid=user_doc["uid"],
            email=user_doc["email"],
            displayName=user_doc.get("display_name", ""),
            isSubscribed=user_doc.get("subscription", False),
            emailVerified=user_doc.get("email_verified", False),
            twoFactorEnabled=user_doc.get("two_factor_enabled", False)
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}"
        )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    current_password: str,
    new_password: str,
    user_data: Dict = Depends(get_verified_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Change password for authenticated user"""
    try:
        # Validate new password strength
        password_validation = ValidationHelpers.validate_password_strength(new_password)
        if not password_validation["is_strong"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "New password does not meet requirements",
                    "suggestions": password_validation["suggestions"]
                }
            )
        
        user_id = user_data["uid"]
        
        # Note: Firebase Admin SDK doesn't provide a way to verify current password
        # This would typically be handled on the client side with Firebase Auth
        # For now, we'll just update the password
        
        # Update password in Firebase Auth
        auth.update_user(user_id, password=new_password)
        
        # Get user document for notification
        user_doc = await AuthHelpers.get_user_document(user_id)
        
        # Send password change notification
        background_tasks.add_task(
            email_service.send_password_changed_notification,
            user_doc["email"],
            user_doc.get("display_name", "")
        )
        
        return MessageResponse(message="Password changed successfully")
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error changing password: {str(e)}"
        )