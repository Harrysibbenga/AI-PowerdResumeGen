from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from firebase_admin import firestore
from typing import Dict
from app.models.auth import Setup2FAResponse, Verify2FARequest, Enable2FARequest, MessageResponse
from app.helpers.auth_helpers import AuthHelpers
from app.services.two_factor_service import two_factor_service
from app.services.email_service import email_service
from app.dependencies.auth_dependencies import get_verified_user, get_current_user

router = APIRouter()

@router.post("/2fa/setup", response_model=Setup2FAResponse)
async def setup_2fa(user_data: Dict = Depends(get_verified_user)):
    user_id = user_data["uid"]
    email = user_data["email"]
    secret = two_factor_service.generate_secret()
    await AuthHelpers.update_user_document(user_id, {"two_factor_secret_temp": secret})
    qr_data = two_factor_service.generate_qr_code(secret, email)
    return Setup2FAResponse(qr_code=qr_data["qr_code"], secret=qr_data["manual_entry_key"])


@router.post("/2fa/enable", response_model=MessageResponse)
async def enable_2fa(request: Enable2FARequest, user_data: Dict = Depends(get_verified_user), background_tasks: BackgroundTasks = BackgroundTasks()):
    user_id = user_data["uid"]
    user_doc = await AuthHelpers.get_user_document(user_id)

    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    secret = user_doc.get("two_factor_secret_temp")
    if not secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA setup not initiated. Please run setup first.")

    if not two_factor_service.verify_code(secret, request.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA code")

    await AuthHelpers.update_user_document(user_id, {
        "two_factor_enabled": True,
        "two_factor_secret": secret,
        "two_factor_secret_temp": firestore.DELETE_FIELD
    })

    background_tasks.add_task(
        email_service.send_2fa_enabled_notification,
        user_doc["email"],
        user_doc.get("display_name", "")
    )

    return MessageResponse(message="2FA enabled successfully")


@router.post("/2fa/disable", response_model=MessageResponse)
async def disable_2fa(request: Verify2FARequest, user_data: Dict = Depends(get_verified_user), background_tasks: BackgroundTasks = BackgroundTasks()):
    user_id = user_data["uid"]
    user_doc = await AuthHelpers.get_user_document(user_id)

    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user_doc.get("two_factor_enabled", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA is not enabled")

    secret = user_doc.get("two_factor_secret")
    if not two_factor_service.verify_code(secret, request.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA code")

    await AuthHelpers.update_user_document(user_id, {
        "two_factor_enabled": False,
        "two_factor_secret": firestore.DELETE_FIELD
    })

    background_tasks.add_task(
        email_service.send_2fa_disabled_notification,
        user_doc["email"],
        user_doc.get("display_name", "")
    )

    return MessageResponse(message="2FA disabled successfully")


@router.post("/2fa/verify", response_model=MessageResponse)
async def verify_2fa(request: Verify2FARequest, user_data: Dict = Depends(get_current_user)):
    user_id = user_data["uid"]
    user_doc = await AuthHelpers.get_user_document(user_id)

    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user_doc.get("two_factor_enabled", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA is not enabled for this user")

    secret = user_doc.get("two_factor_secret")
    if not two_factor_service.verify_code(secret, request.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA code")

    return MessageResponse(message="2FA code verified successfully")
