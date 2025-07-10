from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import Dict
from app.models.auth import SessionResponse, MessageResponse
from app.helpers.auth_helpers import AuthHelpers
from app.core.config import settings
from app.dependencies.auth_dependencies import get_current_user

router = APIRouter()

@router.post("/logout", response_model=MessageResponse)
async def logout(user_data: Dict = Depends(get_current_user)):
    user_id = user_data["uid"]
    try:
        await AuthHelpers.update_user_document(user_id, {
            "last_activity": datetime.now() - timedelta(hours=25)
        })
        return MessageResponse(message="Logged out successfully")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error logging out: {str(e)}")


@router.get("/session/status", response_model=SessionResponse)
async def get_session_status(user_data: Dict = Depends(get_current_user)):
    user_id = user_data["uid"]
    try:
        session_info = await AuthHelpers.check_session_validity(user_id, settings.SESSION_TIMEOUT_HOURS)
        return SessionResponse(
            sessionId=user_id,
            expiresAt=session_info.get("expires_at"),
            isValid=session_info["valid"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error checking session status: {str(e)}")


@router.post("/session/extend", response_model=MessageResponse)
async def extend_session(user_data: Dict = Depends(get_current_user)):
    user_id = user_data["uid"]
    try:
        await AuthHelpers.update_last_activity(user_id)
        new_expires_at = datetime.now() + timedelta(hours=settings.SESSION_TIMEOUT_HOURS)
        return MessageResponse(message=f"Session extended until {new_expires_at.isoformat()}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error extending session: {str(e)}")
