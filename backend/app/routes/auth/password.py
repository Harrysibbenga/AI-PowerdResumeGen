from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from firebase_admin import auth, firestore
from typing import Dict
from app.models.auth import ForgotPasswordRequest, ResetPasswordRequest, MessageResponse
from app.helpers.auth_helpers import AuthHelpers, ValidationHelpers
from app.services.email_service import email_service

router = APIRouter()

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    try:
        try:
            user = auth.get_user_by_email(request.email)
        except auth.UserNotFoundError:
            return MessageResponse(message="If the email exists, a password reset link has been sent.")

        reset_token = AuthHelpers.generate_secure_token()
        await AuthHelpers.update_user_document(user.uid, {
            "password_reset_token": reset_token,
            "password_reset_expires": AuthHelpers.create_expiration_time(1)
        })

        user_doc = await AuthHelpers.get_user_document(user.uid)
        display_name = user_doc.get("display_name", "") if user_doc else ""

        background_tasks.add_task(
            email_service.send_password_reset_email,
            request.email,
            display_name,
            reset_token
        )

        return MessageResponse(message="If the email exists, a password reset link has been sent.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing password reset: {str(e)}")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest, background_tasks: BackgroundTasks):
    password_validation = ValidationHelpers.validate_password_strength(request.newPassword)
    if not password_validation["is_strong"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Password does not meet requirements",
                "suggestions": password_validation["suggestions"]
            }
        )

    user_info = await AuthHelpers.find_user_by_token("password_reset_token", request.token)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    user_data = user_info["data"]
    user_ref = user_info["reference"]

    if AuthHelpers.is_expired(user_data["password_reset_expires"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token has expired")

    auth.update_user(user_data["uid"], password=request.newPassword)

    user_ref.update({
        "password_reset_token": firestore.DELETE_FIELD,
        "password_reset_expires": firestore.DELETE_FIELD
    })

    background_tasks.add_task(
        email_service.send_password_changed_notification,
        user_data["email"],
        user_data.get("display_name", "")
    )

    return MessageResponse(message="Password updated successfully")