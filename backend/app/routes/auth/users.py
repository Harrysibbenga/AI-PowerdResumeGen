from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict
from firebase_admin import auth
from app.models.auth import UserCreate, UserResponse, MessageResponse, UserDocument
from app.helpers.auth_helpers import AuthHelpers, ValidationHelpers
from app.services.email_service import email_service
from app.dependencies.auth_dependencies import get_current_user

router = APIRouter()

@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, background_tasks: BackgroundTasks):
    password_validation = ValidationHelpers.validate_password_strength(user_data.password)
    if not password_validation["is_strong"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Password does not meet requirements",
                "suggestions": password_validation["suggestions"]
            }
        )

    display_name = ValidationHelpers.sanitize_display_name(user_data.displayName or "")

    try:
        user = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=display_name,
            email_verified=False
        )
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating user: {str(e)}")

    verification_token = AuthHelpers.generate_secure_token()
    user_doc = UserDocument(
        uid=user.uid,
        email=user.email,
        display_name=display_name,
        email_verification_token=verification_token,
        email_verification_expires=AuthHelpers.create_expiration_time(24)
    )

    await AuthHelpers.create_user_document(user_doc)

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


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(user_data: Dict = Depends(get_current_user)):
    user_id = user_data["uid"]
    user_doc = await AuthHelpers.get_user_document(user_id)

    if not user_doc:
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


@router.get("/users/me/jwt", response_model=UserResponse)
async def get_current_user_profile_jwt(user_data: Dict = Depends(get_current_user)):
    user_doc = user_data["user_doc"]
    return UserResponse(
        uid=user_doc["uid"],
        email=user_doc["email"],
        displayName=user_doc.get("display_name", ""),
        isSubscribed=user_doc.get("subscription", False),
        emailVerified=user_doc.get("email_verified", False),
        twoFactorEnabled=user_doc.get("two_factor_enabled", False)
    )


@router.get("/user/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, current_user: Dict = Depends(get_current_user)):
    if current_user["uid"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    user_doc = await AuthHelpers.get_user_document(user_id)
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse(
        uid=user_doc["uid"],
        email=user_doc["email"],
        displayName=user_doc.get("display_name", ""),
        isSubscribed=user_doc.get("subscription", False),
        emailVerified=user_doc.get("email_verified", False),
        twoFactorEnabled=user_doc.get("two_factor_enabled", False)
    )


@router.delete("/users/me", response_model=MessageResponse)
async def delete_user(user_data: Dict = Depends(get_current_user)):
    user_id = user_data["uid"]
    try:
        auth.delete_user(user_id)
        await AuthHelpers.delete_user_document(user_id)
        return MessageResponse(message="User deleted successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )