from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from firebase_admin import auth, firestore
from typing import Dict
from app.models.auth import VerifyEmailRequest, MessageResponse
from app.helpers.auth_helpers import AuthHelpers
from app.services.email_service import email_service
from app.dependencies.auth_dependencies import get_current_user

router = APIRouter()

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(request: VerifyEmailRequest, background_tasks: BackgroundTasks):
    user_info = await AuthHelpers.find_user_by_token("email_verification_token", request.token)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")

    user_data = user_info["data"]
    user_ref = user_info["reference"]

    if AuthHelpers.is_expired(user_data["email_verification_expires"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token has expired")

    auth.update_user(user_data["uid"], email_verified=True)
    user_ref.update({
        "email_verified": True,
        "email_verification_token": firestore.DELETE_FIELD,
        "email_verification_expires": firestore.DELETE_FIELD
    })

    background_tasks.add_task(
        email_service.send_welcome_email,
        user_data["email"],
        user_data.get("display_name", "")
    )

    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(user_data: Dict = Depends(get_current_user), background_tasks: BackgroundTasks = BackgroundTasks()):
    user_id = user_data["uid"]
    user_doc = await AuthHelpers.get_user_document(user_id)

    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_doc.get("email_verified", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already verified")

    verification_token = AuthHelpers.generate_secure_token()
    await AuthHelpers.update_user_document(user_id, {
        "email_verification_token": verification_token,
        "email_verification_expires": AuthHelpers.create_expiration_time(24)
    })

    background_tasks.add_task(
        email_service.send_verification_email,
        user_doc["email"],
        user_doc.get("display_name", ""),
        verification_token
    )

    return MessageResponse(message="Verification email sent successfully")
