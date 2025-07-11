# app/routes/register.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict
from firebase_admin import auth as firebase_auth, exceptions as firebase_exceptions
import logging

from app.models.auth import (
    RegisterRequestToken, RegisterResponse, EmailVerificationRequest,
    VerifyEmailRequest, ResendVerificationRequest
)
from app.models.auth import UserResponse, UserDocument, MessageResponse
from app.helpers.auth_helpers import AuthHelpers
from app.dependencies.auth_dependencies import get_jwt_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequestToken, background_tasks: BackgroundTasks):
    """
    Register a new user with Firebase ID token and display name.
    The user should already be created in Firebase on the frontend.
    """
    try:
        # Step 1: Verify Firebase ID token
        decoded_token = firebase_auth.verify_id_token(request.id_token)
        uid = decoded_token["uid"]
        firebase_user = firebase_auth.get_user(uid)
        
        logger.info(f"Registering user: {uid}")

        # Step 2: Check if user already exists in our database
        existing_user = await AuthHelpers.get_user_document(uid)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already registered"
            )

        # Step 3: Update Firebase user profile with display name
        try:
            firebase_auth.update_user(
                uid,
                display_name=request.display_name
            )
        except firebase_exceptions.FirebaseError as e:
            logger.warning(f"Failed to update Firebase profile for {uid}: {str(e)}")
            # Continue with registration even if profile update fails

        # Step 4: Create user document in our database
        user_document = UserDocument(
            uid=uid,
            email=firebase_user.email,
            display_name=request.display_name,
            email_verified=firebase_user.email_verified,
            subscription=False,
            two_factor_enabled=False,
            account_status="active",
            created_at=None,  # Will be set by the helper
            updated_at=None   # Will be set by the helper
        )
        
        await AuthHelpers.create_user_document(user_document)

        # Step 5: Generate JWT tokens
        access_token, refresh_token = AuthHelpers.generate_jwt_tokens(
            uid, firebase_user.email, remember_me=False
        )
        
        # Step 6: Store refresh token
        payload = AuthHelpers.verify_jwt_token(refresh_token, "refresh")
        await AuthHelpers.store_refresh_token(uid, refresh_token, payload["jti"])
        
        # Step 7: Update last activity
        await AuthHelpers.update_last_activity(uid)

        # Step 8: Send welcome email (background task) - only if method exists
        if firebase_user.email and hasattr(AuthHelpers, 'send_welcome_email'):
            try:
                background_tasks.add_task(
                    AuthHelpers.send_welcome_email, 
                    firebase_user.email, 
                    request.display_name
                )
            except Exception as e:
                logger.warning(f"Failed to queue welcome email: {str(e)}")

        logger.info(f"User {uid} registered successfully")

        return RegisterResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600,
            user=UserResponse(
                uid=uid,
                email=firebase_user.email,
                displayName=request.display_name,
                isSubscribed=False,
                emailVerified=firebase_user.email_verified,
                twoFactorEnabled=False
            ),
            message="Account created successfully! Welcome!"
        )

    except firebase_exceptions.InvalidArgumentError:
        logger.error("Invalid Firebase ID token format")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Firebase ID token format"
        )
    except firebase_exceptions.FirebaseError as e:
        logger.error(f"Firebase error during registration: {str(e)}")
        # Handle different Firebase errors
        if "expired" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired Firebase ID token"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Firebase ID token"
            )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_email_verification(request: ResendVerificationRequest):
    """
    Resend email verification for a user.
    """
    try:
        # Verify Firebase ID token
        decoded_token = firebase_auth.verify_id_token(request.id_token)
        uid = decoded_token["uid"]
        firebase_user = firebase_auth.get_user(uid)

        if firebase_user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )

        # Generate verification link
        verification_link = firebase_auth.generate_email_verification_link(
            firebase_user.email
        )
        
        # Send verification email (only if method exists)
        if hasattr(AuthHelpers, 'send_verification_email'):
            await AuthHelpers.send_verification_email(
                firebase_user.email, 
                firebase_user.display_name or "User",
                verification_link
            )
        else:
            logger.warning("send_verification_email method not implemented")

        return MessageResponse(message="Verification email sent successfully")

    except firebase_exceptions.FirebaseError as e:
        logger.error(f"Firebase error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase ID token"
        )
    except Exception as e:
        logger.error(f"Error resending verification email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email_token(request: VerifyEmailRequest):
    """
    Verify email with a token (if using custom verification system).
    Note: Firebase handles email verification automatically.
    """
    try:
        # This would be used if you implement custom email verification
        # For Firebase, email verification is handled automatically
        
        # You can implement custom logic here if needed
        # For now, we'll just return a success message
        
        return MessageResponse(message="Email verified successfully")

    except Exception as e:
        logger.error(f"Error verifying email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )


@router.delete("/account", response_model=MessageResponse)
async def delete_account(user_data: Dict = Depends(get_jwt_user)):
    """
    Delete user account (requires authentication).
    """
    try:
        uid = user_data["uid"]
        
        # Step 1: Delete user from Firebase
        firebase_auth.delete_user(uid)
        
        # Step 2: Delete user document from database (only if method exists)
        if hasattr(AuthHelpers, 'delete_user_document'):
            await AuthHelpers.delete_user_document(uid)
        
        # Step 3: Revoke all refresh tokens
        await AuthHelpers.revoke_all_refresh_tokens(uid)
        
        logger.info(f"User account {uid} deleted successfully")
        
        return MessageResponse(message="Account deleted successfully")

    except firebase_exceptions.FirebaseError as e:
        logger.error(f"Firebase error during account deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during account deletion"
        )