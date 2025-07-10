"""
Authentication dependencies for FastAPI
"""
from fastapi import Depends, HTTPException, status, Request
from typing import Dict, Any
from app.helpers.auth_helpers import AuthHelpers
from app.models.auth import TokenData
from app.core.config import settings

async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user with session management
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict: Decoded token data
        
    Raises:
        HTTPException: If authentication fails or session expired
    """
    # Extract Bearer token from Authorization header
    token = await AuthHelpers.extract_bearer_token(request)
    
    # Verify Firebase token
    token_data = await AuthHelpers.verify_firebase_token(token)
    
    # Check session validity
    session_info = await AuthHelpers.check_session_validity(
        token_data.uid, 
        settings.SESSION_TIMEOUT_HOURS
    )
    
    if not session_info["valid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Session expired: {session_info.get('reason', 'Unknown reason')}"
        )
    
    # Update last activity
    await AuthHelpers.update_last_activity(token_data.uid)
    
    return token_data.firebase_claims

async def get_current_user_no_session_check(request: Request) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user without session management
    (useful for endpoints that need to work even with expired sessions)
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict: Decoded token data
        
    Raises:
        HTTPException: If authentication fails
    """
    # Extract Bearer token from Authorization header
    token = await AuthHelpers.extract_bearer_token(request)
    
    # Verify Firebase token
    token_data = await AuthHelpers.verify_firebase_token(token)
    
    return token_data.firebase_claims

async def get_verified_user(user_data: Dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user with email verification check
    
    Args:
        user_data: Current user data from get_current_user
        
    Returns:
        Dict: User data
        
    Raises:
        HTTPException: If user email is not verified
    """
    user_id = user_data["uid"]
    
    # Get user document to check verification status
    user_doc = await AuthHelpers.get_user_document(user_id)
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user_doc.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return user_data

async def get_admin_user(user_data: Dict = Depends(get_verified_user)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated admin user
    
    Args:
        user_data: Current user data from get_verified_user
        
    Returns:
        Dict: User data
        
    Raises:
        HTTPException: If user is not an admin
    """
    # Check if user has admin role in custom claims
    custom_claims = user_data.get("custom_claims", {})
    
    if not custom_claims.get("admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user_data

async def optional_auth(request: Request) -> Dict[str, Any] | None:
    """
    Optional authentication dependency
    Returns user data if authenticated, None otherwise
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict or None: User data if authenticated, None otherwise
    """
    try:
        return await get_current_user_no_session_check(request)
    except HTTPException:
        return None

class RateLimitDependency:
    """
    Rate limiting dependency
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # In production, use Redis or similar
    
    def __call__(self, request: Request):
        """
        Check rate limit for the request
        
        Args:
            request: FastAPI request object
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        import time
        
        # Get client IP address
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        cutoff_time = current_time - self.window_seconds
        self.requests = {
            ip: timestamps for ip, timestamps in self.requests.items()
            if any(t > cutoff_time for t in timestamps)
        }
        
        # Update timestamps for current IP
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old timestamps for this IP
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if t > cutoff_time
        ]
        
        # Check if rate limit exceeded
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds} seconds"
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)

# Create rate limiting instances
rate_limit_auth = RateLimitDependency(max_requests=5, window_seconds=60)  # 5 requests per minute
rate_limit_email = RateLimitDependency(max_requests=3, window_seconds=300)  # 3 requests per 5 minutes
rate_limit_2fa = RateLimitDependency(max_requests=5, window_seconds=300)  # 5 requests per 5 minutes


async def get_jwt_user(request: Request) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user using JWT tokens
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict: Decoded token data
        
    Raises:
        HTTPException: If authentication fails or session expired
    """
    # Extract Bearer token from Authorization header
    token = await AuthHelpers.extract_bearer_token(request)
    
    # Verify JWT token
    payload = AuthHelpers.verify_jwt_token(token, "access")
    
    # Check if user still exists
    user_doc = await AuthHelpers.get_user_document(payload["uid"])
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Update last activity
    await AuthHelpers.update_last_activity(payload["uid"])
    
    return {
        "uid": payload["uid"],
        "email": payload["email"],
        "user_doc": user_doc
    }

async def get_jwt_verified_user(user_data: Dict = Depends(get_jwt_user)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user with email verification check using JWT
    
    Args:
        user_data: Current user data from get_jwt_user
        
    Returns:
        Dict: User data
        
    Raises:
        HTTPException: If user email is not verified
    """
    user_doc = user_data["user_doc"]
    
    if not user_doc.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return user_data

async def optional_jwt_auth(request: Request) -> Dict[str, Any] | None:
    """
    Optional JWT authentication dependency
    Returns user data if authenticated, None otherwise
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict or None: User data if authenticated, None otherwise
    """
    try:
        return await get_jwt_user(request)
    except HTTPException:
        return None