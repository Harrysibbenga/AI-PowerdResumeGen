import secrets
import hashlib
import jwt
import re
import logging
import pyotp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, List
from fastapi import HTTPException, status, Request

from app.models.auth.token import TokenData
from app.models.auth.user import UserDocument
from app.core.firebase import db, firebase_auth, SERVER_TIMESTAMP, DELETE_FIELD
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthHelpers:
    """Helper class for authentication operations with Firebase Firestore"""

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token using SHA-256"""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def create_expiration_time(hours: int) -> datetime:
        """Create an expiration datetime from current time plus hours"""
        return datetime.now() + timedelta(hours=hours)

    @staticmethod
    def is_expired(expiration_time: datetime) -> bool:
        """Check if a datetime has expired"""
        return not expiration_time or datetime.now() > expiration_time.replace(tzinfo=None)

    @staticmethod
    async def verify_firebase_token(token: str) -> TokenData:
        """Verify Firebase ID token and return TokenData"""
        try:
            decoded = firebase_auth.verify_id_token(token)
            return TokenData(
                uid=decoded["uid"],
                email=decoded.get("email", ""),
                email_verified=decoded.get("email_verified", False),
                firebase_claims=decoded
            )
        except Exception as e:
            logger.error(f"Firebase token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=f"Invalid authentication credentials: {str(e)}"
            )

    @staticmethod
    async def extract_bearer_token(request: Request) -> str:
        """Extract Bearer token from Authorization header"""
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authentication credentials"
            )
        return auth.split("Bearer ")[1]

    @staticmethod
    async def get_user_document(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user document from Firestore"""
        try:
            doc = db.collection("users").document(user_id).get()
            if doc.exists:
                user_data = doc.to_dict()
                # Add document ID to the data
                user_data['uid'] = doc.id
                return user_data
            return None
        except Exception as e:
            logger.error(f"Error retrieving user document for {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error retrieving user document: {str(e)}"
            )

    @staticmethod
    async def update_user_document(user_id: str, data: Dict[str, Any]) -> None:
        """Update user document in Firestore"""
        try:
            # Add updated timestamp
            data['updated_at'] = SERVER_TIMESTAMP
            
            db.collection("users").document(user_id).update(data)
            logger.info(f"User document updated for {user_id}")
        except Exception as e:
            logger.error(f"Error updating user document for {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error updating user document: {str(e)}"
            )

    @staticmethod
    async def create_user_document(user_data: UserDocument) -> None:
        """Create a new user document in Firestore"""
        try:
            # Convert to dict if it's a Pydantic model
            if hasattr(user_data, 'dict'):
                user_dict = user_data.dict(exclude_unset=True)
            else:
                user_dict = user_data
            
            # Add timestamps
            user_dict['created_at'] = SERVER_TIMESTAMP
            user_dict['updated_at'] = SERVER_TIMESTAMP
            
            # Ensure required fields have defaults
            user_dict.setdefault('email_verified', False)
            user_dict.setdefault('two_factor_enabled', False)
            user_dict.setdefault('account_status', 'active')
            user_dict.setdefault('failed_login_attempts', 0)
            user_dict.setdefault('refresh_tokens', [])
            user_dict.setdefault('subscription', 'free')
            
            db.collection("users").document(user_dict['uid']).set(user_dict)
            logger.info(f"User document created for {user_dict['uid']} - {user_dict.get('email')}")
            
        except Exception as e:
            logger.error(f"Error creating user document: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error creating user document: {str(e)}"
            )

    @staticmethod
    async def delete_user_document(user_id: str) -> None:
        """Delete user document from Firestore"""
        try:
            db.collection("users").document(user_id).delete()
            logger.info(f"User document deleted for {user_id}")
        except Exception as e:
            logger.error(f"Error deleting user document for {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error deleting user document: {str(e)}"
            )

    @staticmethod
    async def find_user_by_field(field: str, value: str) -> Optional[Dict[str, Any]]:
        """Find a user by a specific field value"""
        try:
            docs = db.collection("users").where(field, "==", value).limit(1).get()
            if docs:
                doc = docs[0]
                user_data = doc.to_dict()
                user_data['uid'] = doc.id
                return {
                    "data": user_data, 
                    "reference": doc.reference
                }
            return None
        except Exception as e:
            logger.error(f"Error finding user by {field}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error finding user by {field}: {str(e)}"
            )

    @staticmethod
    async def find_user_by_token(field: str, value: str) -> Optional[Dict[str, Any]]:
        """Find user by token field (alias for find_user_by_field for backward compatibility)"""
        return await AuthHelpers.find_user_by_field(field, value)

    @staticmethod
    async def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Find user by email address"""
        return await AuthHelpers.find_user_by_field("email", email)

    @staticmethod
    async def check_session_validity(user_id: str, timeout_hours: int = 24) -> Dict[str, Any]:
        """Check if user session is still valid based on last activity"""
        try:
            user = await AuthHelpers.get_user_document(user_id)
            if not user:
                return {"valid": False, "reason": "User not found"}
            
            last_activity = user.get("last_activity")
            if not last_activity:
                return {"valid": False, "reason": "No activity recorded"}
            
            # Handle Firebase timestamp
            if hasattr(last_activity, 'timestamp'):
                last_dt = datetime.fromtimestamp(last_activity.timestamp())
            else:
                last_dt = last_activity
            
            expires = last_dt + timedelta(hours=timeout_hours)
            now = datetime.now()
            
            return {
                "valid": now <= expires,
                "expires_at": expires,
                "time_remaining": int((expires - now).total_seconds()) if now <= expires else 0
            }
        except Exception as e:
            logger.error(f"Error checking session validity for {user_id}: {str(e)}")
            return {"valid": False, "reason": str(e)}

    @staticmethod
    async def update_last_activity(user_id: str) -> None:
        """Update user's last activity timestamp"""
        try:
            await AuthHelpers.update_user_document(user_id, {"last_activity": SERVER_TIMESTAMP})
        except Exception as e:
            logger.warning(f"Failed to update last activity for user {user_id}: {e}")

    @staticmethod
    async def cleanup_expired_tokens() -> int:
        """Remove expired email verification and password reset tokens"""
        try:
            now = datetime.now()
            count = 0
            
            # Fields to check for expiration
            expiration_fields = ["email_verification_expires", "password_reset_expires"]
            
            for field in expiration_fields:
                # Query for expired tokens
                docs = db.collection("users").where(field, "<=", now).get()
                
                for doc in docs:
                    # Remove both the expiration time and the token
                    token_field = field.replace("expires", "token")
                    update_data = {
                        field: DELETE_FIELD,
                        token_field: DELETE_FIELD
                    }
                    
                    doc.reference.update(update_data)
                    count += 1
                    
            logger.info(f"Cleaned up {count} expired tokens")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")
            return 0

    @staticmethod
    def generate_jwt_tokens(user_id: str, email: str, remember_me: bool = False) -> Tuple[str, str]:
        """Generate JWT access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            "uid": user_id,
            "email": email,
            "type": "access",
            "exp": now + timedelta(hours=1),
            "iat": now
        }
        
        # Refresh token payload
        refresh_payload = {
            "uid": user_id,
            "email": email,
            "type": "refresh",
            "exp": now + timedelta(days=30 if remember_me else 7),
            "iat": now,
            "jti": secrets.token_urlsafe(16)  # JWT ID for token tracking
        }
        
        access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        return access_token, refresh_token

    @staticmethod
    def verify_jwt_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail=f"Invalid token type. Expected {token_type}"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token"
            )

    @staticmethod
    async def store_refresh_token(user_id: str, refresh_token: str, jti: str) -> None:
        """Store refresh token hash in user document"""
        try:
            user_doc = await AuthHelpers.get_user_document(user_id)
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="User not found"
                )

            # Get existing refresh tokens
            refresh_tokens = user_doc.get("refresh_tokens", [])
            
            # Create new token info
            token_info = {
                "jti": jti,
                "created_at": datetime.utcnow(),
                "token_hash": AuthHelpers.hash_token(refresh_token)
            }
            
            # Add new token
            refresh_tokens.append(token_info)
            
            # Keep only the last 5 tokens
            if len(refresh_tokens) > 5:
                refresh_tokens = refresh_tokens[-5:]
            
            await AuthHelpers.update_user_document(user_id, {"refresh_tokens": refresh_tokens})
            
        except Exception as e:
            logger.error(f"Error storing refresh token for {user_id}: {e}")
            raise

    @staticmethod
    async def verify_refresh_token(user_id: str, jti: str, refresh_token: str) -> bool:
        """Verify refresh token exists and is valid"""
        try:
            user_doc = await AuthHelpers.get_user_document(user_id)
            if not user_doc:
                return False
            
            token_hash = AuthHelpers.hash_token(refresh_token)
            refresh_tokens = user_doc.get("refresh_tokens", [])
            
            # Check if token exists and matches
            for token_info in refresh_tokens:
                if (token_info.get("jti") == jti and 
                    token_info.get("token_hash") == token_hash):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying refresh token for {user_id}: {e}")
            return False

    @staticmethod
    async def revoke_refresh_token(user_id: str, jti: str) -> None:
        """Revoke a specific refresh token"""
        try:
            user_doc = await AuthHelpers.get_user_document(user_id)
            if not user_doc:
                return
            
            # Remove token with matching JTI
            refresh_tokens = [
                token for token in user_doc.get("refresh_tokens", [])
                if token.get("jti") != jti
            ]
            
            await AuthHelpers.update_user_document(user_id, {"refresh_tokens": refresh_tokens})
            
        except Exception as e:
            logger.error(f"Error revoking refresh token for {user_id}: {e}")

    @staticmethod
    async def revoke_all_refresh_tokens(user_id: str) -> None:
        """Revoke all refresh tokens for a user"""
        try:
            await AuthHelpers.update_user_document(user_id, {"refresh_tokens": []})
            logger.info(f"All refresh tokens revoked for user {user_id}")
        except Exception as e:
            logger.error(f"Error revoking all refresh tokens for {user_id}: {e}")

    @staticmethod
    async def check_account_lockout(user_id: str) -> Dict[str, Any]:
        """Check if account is locked due to failed login attempts"""
        try:
            user_doc = await AuthHelpers.get_user_document(user_id)
            if not user_doc:
                return {"locked": False}

            failed_attempts = user_doc.get("failed_login_attempts", 0)
            locked_until = user_doc.get("account_locked_until")

            # Check if account is currently locked
            if locked_until:
                # Handle Firebase timestamp
                if hasattr(locked_until, 'timestamp'):
                    locked_until_dt = datetime.fromtimestamp(locked_until.timestamp())
                else:
                    locked_until_dt = locked_until.replace(tzinfo=None)
                
                if datetime.now() < locked_until_dt:
                    return {
                        "locked": True,
                        "locked_until": locked_until_dt,
                        "reason": "Too many failed login attempts"
                    }
                else:
                    # Lock has expired, clear it
                    await AuthHelpers.update_user_document(user_id, {
                        "failed_login_attempts": 0,
                        "account_locked_until": DELETE_FIELD
                    })

            return {"locked": False, "failed_attempts": failed_attempts}
            
        except Exception as e:
            logger.error(f"Error checking account lockout for {user_id}: {e}")
            return {"locked": False}

    @staticmethod
    def verify_2fa_code(secret: str, code: str) -> bool:
        """Verify 2FA TOTP code"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)  # ±30s window
        except Exception as e:
            logger.error(f"Error verifying 2FA code: {e}")
            return False

    @staticmethod
    def generate_2fa_secret() -> str:
        """Generate a new 2FA secret"""
        return pyotp.random_base32()

    @staticmethod
    def generate_2fa_qr_code_url(secret: str, email: str, issuer: str = "YourApp") -> str:
        """Generate QR code URL for 2FA setup"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(email, issuer_name=issuer)

    @staticmethod
    async def handle_failed_login(user_id: str) -> None:
        """Handle failed login attempt and potentially lock account"""
        try:
            user_doc = await AuthHelpers.get_user_document(user_id)
            if not user_doc:
                return
            
            failed_attempts = user_doc.get("failed_login_attempts", 0) + 1
            update_data = {"failed_login_attempts": failed_attempts}
            
            # Lock account after 5 failed attempts
            if failed_attempts >= 5:
                update_data["account_locked_until"] = datetime.now() + timedelta(minutes=30)
                logger.warning(f"Account locked for user {user_id} after {failed_attempts} failed attempts")
            
            await AuthHelpers.update_user_document(user_id, update_data)
            
        except Exception as e:
            logger.error(f"Error handling failed login for {user_id}: {e}")

    @staticmethod
    async def clear_failed_login_attempts(user_id: str) -> None:
        """Clear failed login attempts after successful login"""
        try:
            await AuthHelpers.update_user_document(user_id, {
                "failed_login_attempts": 0,
                "account_locked_until": DELETE_FIELD
            })
        except Exception as e:
            logger.error(f"Error clearing failed login attempts for {user_id}: {e}")

    @staticmethod
    async def set_email_verification_token(user_id: str, hours: int = 24) -> str:
        """Generate and store email verification token"""
        try:
            token = AuthHelpers.generate_secure_token()
            token_hash = AuthHelpers.hash_token(token)
            expiration = AuthHelpers.create_expiration_time(hours)
            
            await AuthHelpers.update_user_document(user_id, {
                "email_verification_token": token_hash,
                "email_verification_expires": expiration
            })
            
            return token
            
        except Exception as e:
            logger.error(f"Error setting email verification token for {user_id}: {e}")
            raise

    @staticmethod
    async def verify_email_verification_token(token: str) -> Optional[str]:
        """Verify email verification token and return user ID"""
        try:
            token_hash = AuthHelpers.hash_token(token)
            user_result = await AuthHelpers.find_user_by_field("email_verification_token", token_hash)
            
            if not user_result:
                return None
            
            user_data = user_result["data"]
            expiration = user_data.get("email_verification_expires")
            
            if not expiration or AuthHelpers.is_expired(expiration):
                return None
            
            return user_data["uid"]
            
        except Exception as e:
            logger.error(f"Error verifying email verification token: {e}")
            return None

    @staticmethod
    async def set_password_reset_token(user_id: str, hours: int = 1) -> str:
        """Generate and store password reset token"""
        try:
            token = AuthHelpers.generate_secure_token()
            token_hash = AuthHelpers.hash_token(token)
            expiration = AuthHelpers.create_expiration_time(hours)
            
            await AuthHelpers.update_user_document(user_id, {
                "password_reset_token": token_hash,
                "password_reset_expires": expiration
            })
            
            return token
            
        except Exception as e:
            logger.error(f"Error setting password reset token for {user_id}: {e}")
            raise

    @staticmethod
    async def verify_password_reset_token(token: str) -> Optional[str]:
        """Verify password reset token and return user ID"""
        try:
            token_hash = AuthHelpers.hash_token(token)
            user_result = await AuthHelpers.find_user_by_field("password_reset_token", token_hash)
            
            if not user_result:
                return None
            
            user_data = user_result["data"]
            expiration = user_data.get("password_reset_expires")
            
            if not expiration or AuthHelpers.is_expired(expiration):
                return None
            
            return user_data["uid"]
            
        except Exception as e:
            logger.error(f"Error verifying password reset token: {e}")
            return None


class ValidationHelpers:
    """Helper class for validation operations"""

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength and return score with suggestions"""
        score = 0
        suggestions = []
        
        # Length check
        if len(password) >= 8:
            score += 1
        else:
            suggestions.append("Password should be at least 8 characters long")
        
        # Uppercase letter check
        if any(c.isupper() for c in password):
            score += 1
        else:
            suggestions.append("Add an uppercase letter")
        
        # Lowercase letter check
        if any(c.islower() for c in password):
            score += 1
        else:
            suggestions.append("Add a lowercase letter")
        
        # Number check
        if any(c.isdigit() for c in password):
            score += 1
        else:
            suggestions.append("Add a number")
        
        # Special character check
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        else:
            suggestions.append("Add a special character")
        
        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]
        
        return {
            "score": score,
            "strength": strength_levels[score],
            "is_strong": score >= 4,
            "suggestions": suggestions
        }

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format using regex"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def sanitize_display_name(name: str) -> str:
        """Sanitize and format display name"""
        if not name:
            return ""
        
        # Remove extra whitespace and limit length
        sanitized = " ".join(name.strip().split())
        return sanitized[:50] if len(sanitized) > 50 else sanitized

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format (basic validation)"""
        if not phone:
            return False
        
        # Remove common formatting characters
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Check if it's a valid international format
        if cleaned.startswith('+'):
            return len(cleaned) >= 10 and len(cleaned) <= 15
        
        # Check if it's a valid national format
        return len(cleaned) >= 10 and len(cleaned) <= 15

    @staticmethod
    def validate_2fa_code(code: str) -> bool:
        """Validate 2FA code format"""
        if not code:
            return False
        
        # Remove spaces and check if it's 6 digits
        cleaned = re.sub(r'\s', '', code)
        return len(cleaned) == 6 and cleaned.isdigit()


class EmailHelpers:
    """Helper class for email operations (placeholder for future implementation)"""

    @staticmethod
    async def send_welcome_email(email: str, display_name: str) -> None:
        """Send welcome email to new user"""
        try:
            # TODO: Implement email sending when SMTP is configured
            logger.info(f"Welcome email would be sent to {email} for user {display_name}")
            
            # When you implement email sending:
            # from app.core.email import send_email
            # await send_email(
            #     to=email,
            #     subject="Welcome to YourApp!",
            #     template="welcome",
            #     context={"display_name": display_name}
            # )
            
        except Exception as e:
            logger.warning(f"Error sending welcome email to {email}: {str(e)}")

    @staticmethod
    async def send_verification_email(email: str, display_name: str, verification_link: str) -> None:
        """Send email verification email"""
        try:
            # TODO: Implement email sending when SMTP is configured
            logger.info(f"Verification email would be sent to {email} for user {display_name}")
            logger.info(f"Verification link: {verification_link}")
            
            # When you implement email sending:
            # from app.core.email import send_email
            # await send_email(
            #     to=email,
            #     subject="Please verify your email address",
            #     template="email_verification",
            #     context={
            #         "display_name": display_name,
            #         "verification_link": verification_link
            #     }
            # )
            
        except Exception as e:
            logger.warning(f"Error sending verification email to {email}: {str(e)}")

    @staticmethod
    async def send_password_reset_email(email: str, display_name: str, reset_link: str) -> None:
        """Send password reset email"""
        try:
            # TODO: Implement email sending when SMTP is configured
            logger.info(f"Password reset email would be sent to {email} for user {display_name}")
            logger.info(f"Reset link: {reset_link}")
            
            # When you implement email sending:
            # from app.core.email import send_email
            # await send_email(
            #     to=email,
            #     subject="Password Reset Request",
            #     template="password_reset",
            #     context={
            #         "display_name": display_name,
            #         "reset_link": reset_link
            #     }
            # )
            
        except Exception as e:
            logger.warning(f"Error sending password reset email to {email}: {str(e)}")

    @staticmethod
    async def send_2fa_setup_email(email: str, display_name: str) -> None:
        """Send 2FA setup notification email"""
        try:
            # TODO: Implement email sending when SMTP is configured
            logger.info(f"2FA setup notification would be sent to {email} for user {display_name}")
            
        except Exception as e:
            logger.warning(f"Error sending 2FA setup email to {email}: {str(e)}")

    @staticmethod
    async def send_security_alert_email(email: str, display_name: str, alert_type: str, details: str) -> None:
        """Send security alert email"""
        try:
            # TODO: Implement email sending when SMTP is configured
            logger.info(f"Security alert ({alert_type}) would be sent to {email} for user {display_name}")
            logger.info(f"Alert details: {details}")
            
        except Exception as e:
            logger.warning(f"Error sending security alert email to {email}: {str(e)}")