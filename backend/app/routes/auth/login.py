from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict
from firebase_admin import auth
from app.models.auth import (
    LoginRequest, LoginWith2FARequest, LoginResponse, MessageResponse,
    RefreshTokenRequest, RefreshTokenResponse, UserResponse, UserDocument
)
from app.helpers.auth_helpers import AuthHelpers
from app.dependencies.auth_dependencies import get_jwt_user

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, background_tasks: BackgroundTasks):
    # Consider adding a background task in the future if needed 
    try:
        try:
            firebase_user = auth.get_user_by_email(request.email)
        except auth.UserNotFoundError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        lockout_status = await AuthHelpers.check_account_lockout(firebase_user.uid)
        if lockout_status["locked"]:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail={
                "message": "Account temporarily locked",
                "locked_until": lockout_status["locked_until"].isoformat()
            })

        user_doc = await AuthHelpers.get_user_document(firebase_user.uid)
        if not user_doc:
            user_document = UserDocument(
                uid=firebase_user.uid,
                email=firebase_user.email,
                display_name=firebase_user.display_name or "",
                email_verified=firebase_user.email_verified
            )
            await AuthHelpers.create_user_document(user_document)
            user_doc = user_document.dict()

        if user_doc.get("two_factor_enabled", False):
            return LoginResponse(
                access_token="",
                refresh_token="",
                expires_in=0,
                user=UserResponse(
                    uid=firebase_user.uid,
                    email=firebase_user.email,
                    displayName=user_doc.get("display_name", ""),
                    isSubscribed=user_doc.get("subscription", False),
                    emailVerified=user_doc.get("email_verified", False),
                    twoFactorEnabled=True
                ),
                requires_2fa=True
            )

        access_token, refresh_token = AuthHelpers.generate_jwt_tokens(
            firebase_user.uid,
            firebase_user.email,
            request.remember_me
        )
        payload = AuthHelpers.verify_jwt_token(refresh_token, "refresh")
        await AuthHelpers.store_refresh_token(firebase_user.uid, refresh_token, payload["jti"])
        await AuthHelpers.clear_failed_login_attempts(firebase_user.uid)
        await AuthHelpers.update_last_activity(firebase_user.uid)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600,
            user=UserResponse(
                uid=firebase_user.uid,
                email=firebase_user.email,
                displayName=user_doc.get("display_name", ""),
                isSubscribed=user_doc.get("subscription", False),
                emailVerified=user_doc.get("email_verified", False),
                twoFactorEnabled=user_doc.get("two_factor_enabled", False)
            )
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during login: {str(e)}")


@router.post("/login/2fa", response_model=LoginResponse)
async def login_with_2fa(request: LoginWith2FARequest):
    try:
        firebase_user = auth.get_user_by_email(request.email)
        lockout_status = await AuthHelpers.check_account_lockout(firebase_user.uid)
        if lockout_status["locked"]:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail={
                "message": "Account temporarily locked",
                "locked_until": lockout_status["locked_until"].isoformat()
            })

        user_doc = await AuthHelpers.get_user_document(firebase_user.uid)
        if not user_doc or not user_doc.get("two_factor_enabled", False):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA is not enabled")

        if not request.two_factor_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA code is required")

        secret = user_doc.get("two_factor_secret")
        if not AuthHelpers.verify_2fa_code(secret, request.two_factor_code):
            await AuthHelpers.handle_failed_login(firebase_user.uid)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid 2FA code")

        access_token, refresh_token = AuthHelpers.generate_jwt_tokens(
            firebase_user.uid,
            firebase_user.email,
            request.remember_me
        )
        payload = AuthHelpers.verify_jwt_token(refresh_token, "refresh")
        await AuthHelpers.store_refresh_token(firebase_user.uid, refresh_token, payload["jti"])
        await AuthHelpers.clear_failed_login_attempts(firebase_user.uid)
        await AuthHelpers.update_last_activity(firebase_user.uid)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600,
            user=UserResponse(
                uid=firebase_user.uid,
                email=firebase_user.email,
                displayName=user_doc.get("display_name", ""),
                isSubscribed=user_doc.get("subscription", False),
                emailVerified=user_doc.get("email_verified", False),
                twoFactorEnabled=True
            )
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during 2FA login: {str(e)}")


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    try:
        payload = AuthHelpers.verify_jwt_token(request.refresh_token, "refresh")
        user_id = payload["uid"]
        jti = payload["jti"]

        if not await AuthHelpers.verify_refresh_token(user_id, jti, request.refresh_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user_doc = await AuthHelpers.get_user_document(user_id)
        if not user_doc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        access_token, new_refresh_token = AuthHelpers.generate_jwt_tokens(user_id, payload["email"])
        await AuthHelpers.revoke_refresh_token(user_id, jti)
        new_payload = AuthHelpers.verify_jwt_token(new_refresh_token, "refresh")
        await AuthHelpers.store_refresh_token(user_id, new_refresh_token, new_payload["jti"])
        await AuthHelpers.update_last_activity(user_id)

        return RefreshTokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=3600
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@router.post("/logout/all", response_model=MessageResponse)
async def logout_all_devices(user_data: Dict = Depends(get_jwt_user)):
    try:
        await AuthHelpers.revoke_all_refresh_tokens(user_data["uid"])
        return MessageResponse(message="Logged out from all devices successfully")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during logout: {str(e)}")
