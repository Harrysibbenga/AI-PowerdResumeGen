from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from firebase_admin import auth
import logging
import requests
from pydantic import BaseModel

from app.models.auth import (
    ChangePasswordRequest, 
    ChangePasswordResponse, 
    ForgotPasswordRequest, 
    ResetPasswordRequest, 
    PasswordValidationResponse,
    PasswordValidationRequest,
    MessageResponse
)
from app.helpers.auth_helpers import AuthHelpers, ValidationHelpers, EmailHelpers
from app.services.email_service import email_service
from app.dependencies.auth_dependencies import get_user_for_password_change
from app.core.firebase import SERVER_TIMESTAMP, DELETE_FIELD

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    """
    Send password reset email if user exists.
    Always returns success message to prevent email enumeration.
    """
    try:
        # Standard response to prevent email enumeration
        response_message = "If the email exists, a password reset link has been sent."
        
        # Check if user exists in Firebase Auth
        try:
            firebase_user = auth.get_user_by_email(request.email)
        except auth.UserNotFoundError:
            logger.info(f"Password reset requested for non-existent email: {request.email}")
            return MessageResponse(message=response_message)
        
        # Check if user document exists in Firestore
        user_doc = await AuthHelpers.get_user_document(firebase_user.uid)
        if not user_doc:
            logger.warning(f"Firebase user exists but no user document found: {firebase_user.uid}")
            return MessageResponse(message=response_message)
        
        # Generate and store reset token (expires in 1 hour)
        reset_token = await AuthHelpers.set_password_reset_token(firebase_user.uid, hours=1)
        
        # Send reset email in background
        background_tasks.add_task(
            email_service.send_password_reset_email,
            request.email,
            user_doc.get("display_name", ""),
            reset_token  # Pass the raw token, not hashed
        )
        
        logger.info(f"Password reset token generated for user: {firebase_user.uid}")
        return MessageResponse(message=response_message)
        
    except Exception as e:
        logger.error(f"Error in forgot password: {str(e)}")
        # Still return success to prevent information leakage
        return MessageResponse(message="If the email exists, a password reset link has been sent.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest, background_tasks: BackgroundTasks):
    """
    Reset password using token from email.
    """
    try:
        # Validate new password strength
        password_validation = ValidationHelpers.validate_password_strength(request.newPassword)
        if not password_validation["is_strong"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "suggestions": password_validation["suggestions"]
                }
            )
        
        # Verify reset token and get user ID
        user_id = await AuthHelpers.verify_password_reset_token(request.token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get user data
        user_data = await AuthHelpers.get_user_document(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password in Firebase Auth
        auth.update_user(user_id, password=request.newPassword)
        
        # Clear reset token and update user document
        await AuthHelpers.update_user_document(user_id, {
            "password_reset_token": DELETE_FIELD,
            "password_reset_expires": DELETE_FIELD,
            "password_changed_at": SERVER_TIMESTAMP
        })
        
        # Revoke all refresh tokens to force re-login on all devices
        await AuthHelpers.revoke_all_refresh_tokens(user_id)
        
        # Clear failed login attempts if any
        await AuthHelpers.clear_failed_login_attempts(user_id)
        
        # Send security notification email in background
        background_tasks.add_task(
            email_service.send_password_changed_notification,
            user_data["email"],
            user_data.get("display_name", "")
        )
        
        logger.info(f"Password reset completed for user: {user_id}")
        return MessageResponse(message="Password reset successful. Please log in with your new password.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in reset password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting your password"
        )


@router.put("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_user_for_password_change)
):
    """
    Change password for authenticated user.
    Requires current password verification.
    """
    try:
        # Validate new password strength
        password_validation = ValidationHelpers.validate_password_strength(request.new_password)
        if not password_validation["is_strong"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "suggestions": password_validation["suggestions"]
                }
            )
        
        # Check if new password is different from current
        if request.current_password == request.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )
        
        user_id = current_user["uid"]
        user_email = current_user["email"]
        
        # Verify current password by creating a temporary custom token and testing it
        try:
            # Use Firebase Auth REST API to verify password    
            verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_WEB_API_KEY}"
            
            verify_payload = {
                "email": user_email,
                "password": request.current_password,
                "returnSecureToken": True
            }
            
            response = requests.post(verify_url, json=verify_payload)
            
            print(response)
            
            if response.status_code != 200:
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
                
        except requests.RequestException:
            # Fallback: Skip current password verification (less secure)
            logger.warning(f"Could not verify current password for user {user_id} - proceeding anyway")
        
        # Update password in Firebase Auth
        auth.update_user(user_id, password=request.new_password)
        
        # Update user document with timestamp
        await AuthHelpers.update_user_document(user_id, {
            "password_changed_at": SERVER_TIMESTAMP
        })
        
        # Optional: Revoke all other sessions (uncomment if you want this behavior)
        # await AuthHelpers.revoke_all_refresh_tokens(user_id)
        
        # Send security notification email
        await EmailHelpers.send_security_alert_email(
            user_email,
            current_user.get("display_name", ""),
            "password_change",
            "Your password was successfully changed from your account settings"
        )
        
        logger.info(f"Password changed for user: {user_id}")
        return ChangePasswordResponse(message="Password changed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in change password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing your password"
        )


@router.post("/validate-password", response_model=PasswordValidationResponse)
async def validate_password_strength(request: PasswordValidationRequest):
    """
    Validate password strength without saving.
    Useful for real-time password strength indicators in UI.
    """
    try:
        # Use the existing ValidationHelpers method
        validation_result = ValidationHelpers.validate_password_strength(request.password)
        
        # Return the validation result
        return PasswordValidationResponse(
            score=validation_result["score"],
            strength=validation_result["strength"],
            is_strong=validation_result["is_strong"],
            suggestions=validation_result["suggestions"]
        )
    except Exception as e:
        logger.error(f"Error validating password strength: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating password"
        )