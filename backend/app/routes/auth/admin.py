from fastapi import APIRouter, HTTPException, status
from app.models.auth import MessageResponse
from app.helpers.auth_helpers import AuthHelpers

router = APIRouter()

@router.post("/cleanup-tokens", response_model=MessageResponse)
async def cleanup_expired_tokens():
    try:
        cleaned_count = await AuthHelpers.cleanup_expired_tokens()
        return MessageResponse(message=f"Cleaned up {cleaned_count} expired tokens")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error cleaning up tokens: {str(e)}")


@router.get("/health", response_model=MessageResponse)
async def health_check():
    return MessageResponse(message="Authentication service is healthy")
