"""
Authentication dependencies for FastAPI
"""
from fastapi import Depends, HTTPException, status, Request
from typing import Dict, Any, Optional, Union
import logging
from app.helpers.auth_helpers import AuthHelpers
from app.models.auth import TokenData
from app.core.config import settings

logger = logging.getLogger(__name__)

# =================== CORE AUTH DEPENDENCIES ===================

async def get_firebase_user(request: Request) -> Dict[str, Any]:
    """
    Get current user using Firebase ID token verification.
    Returns user document from database.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict: User document from Firestore
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Extract Bearer token from Authorization header
        token = await AuthHelpers.extract_bearer_token(request)
        
        # Verify Firebase ID token
        token_data = await AuthHelpers.verify_firebase_token(token)
        
        # Get user document from database
        user_doc = await AuthHelpers.get_user_document(token_data.uid)
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update last activity
        await AuthHelpers.update_last_activity(token_data.uid)
        
        return user_doc
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_firebase_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


async def get_jwt_user(request: Request) -> Dict[str, Any]:
    """
    Get current user using JWT access token verification.
    Returns user document from database.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict: User document from Firestore
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Extract Bearer token from Authorization header
        token = await AuthHelpers.extract_bearer_token(request)
        
        # Verify JWT token
        payload = AuthHelpers.verify_jwt_token(token, "access")
        
        # Get user document from database
        user_doc = await AuthHelpers.get_user_document(payload["uid"])
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update last activity
        await AuthHelpers.update_last_activity(payload["uid"])
        
        return user_doc
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_jwt_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


async def get_firebase_user_with_session(request: Request) -> Dict[str, Any]:
    """
    Get current user with Firebase token + session validity check.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict: User document from Firestore
        
    Raises:
        HTTPException: If authentication fails or session expired
    """
    try:
        # Extract Bearer token from Authorization header
        token = await AuthHelpers.extract_bearer_token(request)
        
        # Verify Firebase token
        token_data = await AuthHelpers.verify_firebase_token(token)
        
        # Check session validity (if SESSION_TIMEOUT_HOURS is configured)
        session_timeout = getattr(settings, 'SESSION_TIMEOUT_HOURS', 24)
        session_info = await AuthHelpers.check_session_validity(
            token_data.uid, 
            session_timeout
        )
        
        if not session_info["valid"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Session expired: {session_info.get('reason', 'Unknown reason')}"
            )
        
        # Get user document from database
        user_doc = await AuthHelpers.get_user_document(token_data.uid)
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update last activity
        await AuthHelpers.update_last_activity(token_data.uid)
        
        return user_doc
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_firebase_user_with_session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


# =================== VERIFICATION DEPENDENCIES ===================

async def get_verified_user(user_data: Dict = Depends(get_firebase_user)) -> Dict[str, Any]:
    """
    Get current authenticated user with email verification check.
    
    Args:
        user_data: Current user data from get_firebase_user
        
    Returns:
        Dict: User data
        
    Raises:
        HTTPException: If user email is not verified
    """
    if not user_data.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return user_data


async def get_verified_jwt_user(user_data: Dict = Depends(get_jwt_user)) -> Dict[str, Any]:
    """
    Get current authenticated user with email verification check using JWT.
    
    Args:
        user_data: Current user data from get_jwt_user
        
    Returns:
        Dict: User data
        
    Raises:
        HTTPException: If user email is not verified
    """
    if not user_data.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return user_data


# =================== ADMIN DEPENDENCIES ===================

async def get_admin_user(user_data: Dict = Depends(get_verified_user)) -> Dict[str, Any]:
    """
    Get current authenticated admin user.
    
    Args:
        user_data: Current user data from get_verified_user
        
    Returns:
        Dict: User data
        
    Raises:
        HTTPException: If user is not an admin
    """
    # Check admin status in user document
    if not user_data.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user_data


async def get_admin_jwt_user(user_data: Dict = Depends(get_verified_jwt_user)) -> Dict[str, Any]:
    """
    Get current authenticated admin user using JWT.
    
    Args:
        user_data: Current user data from get_verified_jwt_user
        
    Returns:
        Dict: User data
        
    Raises:
        HTTPException: If user is not an admin
    """
    # Check admin status in user document
    if not user_data.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user_data


# =================== OPTIONAL DEPENDENCIES ===================

async def get_optional_firebase_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated with Firebase token, otherwise return None.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Optional[Dict]: User data if authenticated, None otherwise
    """
    try:
        return await get_firebase_user(request)
    except HTTPException:
        return None


async def get_optional_jwt_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated with JWT token, otherwise return None.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Optional[Dict]: User data if authenticated, None otherwise
    """
    try:
        return await get_jwt_user(request)
    except HTTPException:
        return None


# =================== BACKWARD COMPATIBILITY ===================

# Aliases for backward compatibility
get_current_user = get_firebase_user_with_session  # Your original implementation
get_current_user_firebase = get_firebase_user
get_current_user_no_session_check = get_firebase_user
get_optional_user = get_optional_firebase_user
optional_auth = get_optional_firebase_user
optional_jwt_auth = get_optional_jwt_user


# =================== RATE LIMITING ===================

from typing import Dict as typing_Dict
import time
from threading import Lock

class ThreadSafeRateLimit:
    """
    Thread-safe in-memory rate limiter.
    For production, use Redis-based rate limiting.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: typing_Dict[str, list] = {}
        self._lock = Lock()
    
    def __call__(self, request: Request):
        """
        Check rate limit for the request.
        
        Args:
            request: FastAPI request object
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        # Get client IP address
        client_ip = request.client.host
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        with self._lock:
            # Initialize if not exists
            if client_ip not in self.requests:
                self.requests[client_ip] = []
            
            # Remove old timestamps
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
            
            # Cleanup old IPs periodically (every 100 requests)
            if len(self.requests) % 100 == 0:
                self._cleanup_old_ips(cutoff_time)
    
    def _cleanup_old_ips(self, cutoff_time: float):
        """Remove IPs with no recent requests."""
        ips_to_remove = [
            ip for ip, timestamps in self.requests.items()
            if not timestamps or max(timestamps) < cutoff_time
        ]
        for ip in ips_to_remove:
            del self.requests[ip]


# Create rate limiting instances
rate_limit_auth = ThreadSafeRateLimit(max_requests=5, window_seconds=60)      # 5 per minute
rate_limit_email = ThreadSafeRateLimit(max_requests=3, window_seconds=300)    # 3 per 5 minutes
rate_limit_password = ThreadSafeRateLimit(max_requests=3, window_seconds=300) # 3 per 5 minutes
rate_limit_2fa = ThreadSafeRateLimit(max_requests=5, window_seconds=300)      # 5 per 5 minutes


# =================== UTILITY DEPENDENCIES ===================

def require_rate_limit(limiter: ThreadSafeRateLimit):
    """
    Create a rate limit dependency.
    
    Args:
        limiter: Rate limiter instance
        
    Returns:
        Dependency function
    """
    def dependency(request: Request):
        return limiter(request)
    return Depends(dependency)


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Client IP address
    """
    # Check for forwarded headers first (if behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return request.client.host


# =================== SPECIALIZED DEPENDENCIES ===================

async def get_user_for_password_change(request: Request) -> Dict[str, Any]:
    """
    Specialized dependency for password change operations.
    Uses JWT authentication.
    """
    return await get_jwt_user(request)


async def get_user_for_profile_update(request: Request) -> Dict[str, Any]:
    """
    Specialized dependency for profile updates.
    Uses Firebase authentication with verification check.
    """
    user_data = await get_firebase_user(request)
    
    # Ensure email is verified for profile updates
    if not user_data.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required for profile updates"
        )
    
    return user_data