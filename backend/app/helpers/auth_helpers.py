"""
Authentication helper functions and utilities
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request

# Import our models and Firebase setup
from app.models.auth_models import TokenData, UserDocument
from app.core.firebase import db, firebase_auth, SERVER_TIMESTAMP, DELETE_FIELD

class AuthHelpers:
    """Helper class for authentication operations"""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token for secure storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def create_expiration_time(hours: int) -> datetime:
        """Create expiration timestamp"""
        return datetime.now() + timedelta(hours=hours)
    
    @staticmethod
    def is_expired(expiration_time: datetime) -> bool:
        """Check if a timestamp has expired"""
        if expiration_time is None:
            return True
        return datetime.now() > expiration_time.replace(tzinfo=None)
    
    @staticmethod
    async def verify_firebase_token(token: str) -> TokenData:
        """
        Verify Firebase ID token and return decoded data
        
        Args:
            token: Firebase ID token
            
        Returns:
            TokenData: Decoded token information
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            
            return TokenData(
                uid=decoded_token["uid"],
                email=decoded_token.get("email", ""),
                email_verified=decoded_token.get("email_verified", False),
                firebase_claims=decoded_token
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication credentials: {str(e)}"
            )
    
    @staticmethod
    async def extract_bearer_token(request: Request) -> str:
        """
        Extract Bearer token from Authorization header
        
        Args:
            request: FastAPI request object
            
        Returns:
            str: The extracted token
            
        Raises:
            HTTPException: If Authorization header is missing or invalid
        """
        authorization = request.headers.get("Authorization")
        
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return authorization.split("Bearer ")[1]
    
    @staticmethod
    async def get_user_document(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user document from Firestore
        
        Args:
            user_id: User's Firebase UID
            
        Returns:
            Dict or None: User document data
        """
        try:
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving user document: {str(e)}"
            )
    
    @staticmethod
    async def update_user_document(user_id: str, update_data: Dict[str, Any]) -> None:
        """
        Update user document in Firestore
        
        Args:
            user_id: User's Firebase UID
            update_data: Data to update
        """
        try:
            user_ref = db.collection("users").document(user_id)
            user_ref.update(update_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating user document: {str(e)}"
            )
    
    @staticmethod
    async def create_user_document(user_data: UserDocument) -> None:
        """
        Create user document in Firestore
        
        Args:
            user_data: User document data
        """
        try:
            user_ref = db.collection("users").document(user_data.uid)
            user_ref.set(user_data.dict(exclude_unset=True))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user document: {str(e)}"
            )
    
    @staticmethod
    async def delete_user_document(user_id: str) -> None:
        """
        Delete user document from Firestore
        
        Args:
            user_id: User's Firebase UID
        """
        try:
            db.collection("users").document(user_id).delete()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting user document: {str(e)}"
            )
    
    @staticmethod
    async def find_user_by_token(token_field: str, token_value: str) -> Optional[Dict[str, Any]]:
        """
        Find user by a specific token field
        
        Args:
            token_field: Field name containing the token
            token_value: Token value to search for
            
        Returns:
            Dict or None: User document data and reference
        """
        try:
            users_ref = db.collection("users")
            query = users_ref.where(token_field, "==", token_value).limit(1)
            docs = query.get()
            
            if docs:
                doc = docs[0]
                return {
                    "data": doc.to_dict(),
                    "reference": doc.reference
                }
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error finding user by token: {str(e)}"
            )
    
    @staticmethod
    async def check_session_validity(user_id: str, session_timeout_hours: int = 24) -> Dict[str, Any]:
        """
        Check if user session is still valid
        
        Args:
            user_id: User's Firebase UID
            session_timeout_hours: Session timeout in hours
            
        Returns:
            Dict: Session validity information
        """
        try:
            user_data = await AuthHelpers.get_user_document(user_id)
            
            if not user_data:
                return {"valid": False, "reason": "User not found"}
            
            last_activity = user_data.get("last_activity")
            
            if not last_activity:
                return {"valid": False, "reason": "No activity recorded"}
            
            # Handle Firestore timestamp
            if hasattr(last_activity, 'timestamp'):
                # Convert Firestore timestamp to datetime
                last_activity_dt = datetime.fromtimestamp(last_activity.timestamp())
            else:
                # Assume it's already a datetime
                last_activity_dt = last_activity.replace(tzinfo=None) if hasattr(last_activity, 'replace') else last_activity
            
            # Check if session expired
            session_expires = last_activity_dt + timedelta(hours=session_timeout_hours)
            current_time = datetime.now()
            
            if current_time > session_expires:
                return {
                    "valid": False, 
                    "reason": "Session expired",
                    "expired_at": session_expires
                }
            
            return {
                "valid": True,
                "expires_at": session_expires,
                "time_remaining": int((session_expires - current_time).total_seconds())
            }
        except Exception as e:
            return {"valid": False, "reason": f"Error checking session: {str(e)}"}
    
    @staticmethod
    async def update_last_activity(user_id: str) -> None:
        """
        Update user's last activity timestamp
        
        Args:
            user_id: User's Firebase UID
        """
        try:
            await AuthHelpers.update_user_document(user_id, {
                "last_activity": SERVER_TIMESTAMP
            })
        except Exception as e:
            # Log the error but don't raise an exception to avoid breaking the request
            import logging
            logging.getLogger(__name__).warning(f"Failed to update last activity for user {user_id}: {e}")
    
    @staticmethod
    async def cleanup_expired_tokens() -> int:
        """
        Clean up expired tokens from all users (utility function)
        
        Returns:
            int: Number of cleaned up records
        """
        try:
            users_ref = db.collection("users")
            current_time = datetime.now()
            cleanup_count = 0
            
            # Get all users with verification tokens
            verification_query = users_ref.where("email_verification_expires", "<=", current_time)
            verification_docs = verification_query.get()
            
            for doc in verification_docs:
                doc.reference.update({
                    "email_verification_token": DELETE_FIELD,
                    "email_verification_expires": DELETE_FIELD
                })
                cleanup_count += 1
            
            # Get all users with reset tokens
            reset_query = users_ref.where("password_reset_expires", "<=", current_time)
            reset_docs = reset_query.get()
            
            for doc in reset_docs:
                doc.reference.update({
                    "password_reset_token": DELETE_FIELD,
                    "password_reset_expires": DELETE_FIELD
                })
                cleanup_count += 1
            
            return cleanup_count
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error cleaning up expired tokens: {e}")
            return 0

class ValidationHelpers:
    """Helper class for validation operations"""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Dict: Validation result with score and suggestions
        """
        score = 0
        suggestions = []
        
        if len(password) >= 8:
            score += 1
        else:
            suggestions.append("Password should be at least 8 characters long")
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            suggestions.append("Password should contain at least one uppercase letter")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            suggestions.append("Password should contain at least one lowercase letter")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            suggestions.append("Password should contain at least one number")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        else:
            suggestions.append("Password should contain at least one special character")
        
        strength_levels = {
            0: "Very Weak",
            1: "Weak", 
            2: "Fair",
            3: "Good",
            4: "Strong",
            5: "Very Strong"
        }
        
        return {
            "score": score,
            "strength": strength_levels[score],
            "is_strong": score >= 4,
            "suggestions": suggestions
        }
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Validate email format (basic validation)
        
        Args:
            email: Email to validate
            
        Returns:
            bool: True if valid format
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_display_name(display_name: str) -> str:
        """
        Sanitize display name input
        
        Args:
            display_name: Display name to sanitize
            
        Returns:
            str: Sanitized display name
        """
        if not display_name:
            return ""
        
        # Remove excessive whitespace and limit length
        sanitized = " ".join(display_name.strip().split())
        return sanitized[:50]  # Limit to 50 characters