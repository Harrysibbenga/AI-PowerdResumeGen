import secrets
import hashlib
import jwt
import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, List
from fastapi import HTTPException, status, Request

from app.models.auth.token import TokenData
from app.models.auth.user import UserDocument
from app.core.firebase import db, firebase_auth, SERVER_TIMESTAMP, DELETE_FIELD
from app.core.config import settings


class AuthHelpers:
    """Helper class for authentication operations"""

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def create_expiration_time(hours: int) -> datetime:
        return datetime.now() + timedelta(hours=hours)

    @staticmethod
    def is_expired(expiration_time: datetime) -> bool:
        return not expiration_time or datetime.now() > expiration_time.replace(tzinfo=None)

    @staticmethod
    async def verify_firebase_token(token: str) -> TokenData:
        try:
            decoded = firebase_auth.verify_id_token(token)
            return TokenData(
                uid=decoded["uid"],
                email=decoded.get("email", ""),
                email_verified=decoded.get("email_verified", False),
                firebase_claims=decoded
            )
        except Exception as e:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid authentication credentials: {str(e)}")

    @staticmethod
    async def extract_bearer_token(request: Request) -> str:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid authentication credentials")
        return auth.split("Bearer ")[1]

    @staticmethod
    async def get_user_document(user_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = db.collection("users").document(user_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error retrieving user document: {str(e)}")

    @staticmethod
    async def update_user_document(user_id: str, data: Dict[str, Any]) -> None:
        try:
            db.collection("users").document(user_id).update(data)
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error updating user document: {str(e)}")

    @staticmethod
    async def create_user_document(user_data: UserDocument) -> None:
        try:
            db.collection("users").document(user_data.uid).set(user_data.dict(exclude_unset=True))
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error creating user document: {str(e)}")

    @staticmethod
    async def delete_user_document(user_id: str) -> None:
        try:
            db.collection("users").document(user_id).delete()
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error deleting user document: {str(e)}")

    @staticmethod
    async def find_user_by_token(field: str, value: str) -> Optional[Dict[str, Any]]:
        try:
            docs = db.collection("users").where(field, "==", value).limit(1).get()
            if docs:
                doc = docs[0]
                return {"data": doc.to_dict(), "reference": doc.reference}
            return None
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error finding user by token: {str(e)}")

    @staticmethod
    async def check_session_validity(user_id: str, timeout_hours: int = 24) -> Dict[str, Any]:
        try:
            user = await AuthHelpers.get_user_document(user_id)
            if not user:
                return {"valid": False, "reason": "User not found"}
            last = user.get("last_activity")
            if not last:
                return {"valid": False, "reason": "No activity recorded"}
            last_dt = datetime.fromtimestamp(last.timestamp()) if hasattr(last, 'timestamp') else last
            expires = last_dt + timedelta(hours=timeout_hours)
            now = datetime.now()
            return {"valid": now <= expires, "expires_at": expires, "time_remaining": int((expires - now).total_seconds())}
        except Exception as e:
            return {"valid": False, "reason": str(e)}

    @staticmethod
    async def update_last_activity(user_id: str) -> None:
        try:
            await AuthHelpers.update_user_document(user_id, {"last_activity": SERVER_TIMESTAMP})
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to update last activity for user {user_id}: {e}")

    @staticmethod
    async def cleanup_expired_tokens() -> int:
        try:
            now = datetime.now()
            count = 0
            for field in ["email_verification_expires", "password_reset_expires"]:
                docs = db.collection("users").where(field, "<=", now).get()
                for doc in docs:
                    update = {
                        field: DELETE_FIELD,
                        field.replace("expires", "token"): DELETE_FIELD
                    }
                    doc.reference.update(update)
                    count += 1
            return count
        except Exception as e:
            logging.getLogger(__name__).error(f"Error cleaning up expired tokens: {e}")
            return 0

    @staticmethod
    def generate_jwt_tokens(user_id: str, email: str, remember_me: bool = False) -> Tuple[str, str]:
        access = {
            "uid": user_id, "email": email, "type": "access",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        refresh = {
            "uid": user_id, "email": email, "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=30 if remember_me else 7),
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        return (
            jwt.encode(access, settings.JWT_SECRET_KEY, algorithm="HS256"),
            jwt.encode(refresh, settings.JWT_SECRET_KEY, algorithm="HS256")
        )

    @staticmethod
    def verify_jwt_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != token_type:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid token type. Expected {token_type}")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    @staticmethod
    async def store_refresh_token(user_id: str, refresh_token: str, jti: str) -> None:
        try:
            user_doc = await AuthHelpers.get_user_document(user_id)
            if not user_doc:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

            refresh_tokens = user_doc.get("refresh_tokens", [])
            token_info = {
                "jti": jti,
                "created_at": datetime.utcnow(),
                "token_hash": AuthHelpers.hash_token(refresh_token)
            }
            refresh_tokens.append(token_info)
            if len(refresh_tokens) > 5:
                refresh_tokens = refresh_tokens[-5:]
            await AuthHelpers.update_user_document(user_id, {"refresh_tokens": refresh_tokens})
        except Exception as e:
            logging.getLogger(__name__).error(f"Error storing refresh token: {e}")

    @staticmethod
    async def verify_refresh_token(user_id: str, jti: str, refresh_token: str) -> bool:
        try:
            user_doc = await AuthHelpers.get_user_document(user_id)
            if not user_doc:
                return False
            token_hash = AuthHelpers.hash_token(refresh_token)
            for token_info in user_doc.get("refresh_tokens", []):
                if token_info.get("jti") == jti and token_info.get("token_hash") == token_hash:
                    return True
            return False
        except Exception:
            return False

    @staticmethod
    async def revoke_refresh_token(user_id: str, jti: str) -> None:
        try:
            user_doc = await AuthHelpers.get_user_document(user_id)
            if not user_doc:
                return
            refresh_tokens = [t for t in user_doc.get("refresh_tokens", []) if t.get("jti") != jti]
            await AuthHelpers.update_user_document(user_id, {"refresh_tokens": refresh_tokens})
        except Exception as e:
            logging.getLogger(__name__).error(f"Error revoking refresh token: {e}")

    @staticmethod
    async def revoke_all_refresh_tokens(user_id: str) -> None:
        try:
            await AuthHelpers.update_user_document(user_id, {"refresh_tokens": []})
        except Exception as e:
            logging.getLogger(__name__).error(f"Error revoking all refresh tokens: {e}")

    @staticmethod
    async def check_account_lockout(user_id: str) -> Dict[str, Any]:
        try:
            user_doc = await AuthHelpers.get_user_document(user_id)
            if not user_doc:
                return {"locked": False}

            failed_attempts = user_doc.get("failed_login_attempts", 0)
            locked_until = user_doc.get("account_locked_until")

            if locked_until and datetime.now() < locked_until.replace(tzinfo=None):
                return {
                    "locked": True,
                    "locked_until": locked_until,
                    "reason": "Too many failed login attempts"
                }

            if locked_until and datetime.now() >= locked_until.replace(tzinfo=None):
                await AuthHelpers.update_user_document(user_id, {
                    "failed_login_attempts": 0,
                    "account_locked_until": DELETE_FIELD
                })

            return {"locked": False, "failed_attempts": failed_attempts}
        except Exception:
            return {"locked": False}

    @staticmethod
    async def handle_failed_login(user_id: str) -> None:
        try:
            user_doc = await AuthHelpers.get_user_document(user_id)
            if not user_doc:
                return
            failed_attempts = user_doc.get("failed_login_attempts", 0) + 1
            update_data = {"failed_login_attempts": failed_attempts}
            if failed_attempts >= 5:
                update_data["account_locked_until"] = datetime.now() + timedelta(minutes=30)
            await AuthHelpers.update_user_document(user_id, update_data)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error handling failed login: {e}")

    @staticmethod
    async def clear_failed_login_attempts(user_id: str) -> None:
        try:
            await AuthHelpers.update_user_document(user_id, {
                "failed_login_attempts": 0,
                "account_locked_until": DELETE_FIELD
            })
        except Exception as e:
            logging.getLogger(__name__).error(f"Error clearing failed login attempts: {e}")



class ValidationHelpers:
    """Helper class for validation operations"""

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        score, suggestions = 0, []
        if len(password) >= 8: score += 1
        else: suggestions.append("Password should be at least 8 characters long")
        if any(c.isupper() for c in password): score += 1
        else: suggestions.append("Add an uppercase letter")
        if any(c.islower() for c in password): score += 1
        else: suggestions.append("Add a lowercase letter")
        if any(c.isdigit() for c in password): score += 1
        else: suggestions.append("Add a number")
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 1
        else: suggestions.append("Add a special character")
        levels = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]
        return {
            "score": score,
            "strength": levels[score],
            "is_strong": score >= 4,
            "suggestions": suggestions
        }

    @staticmethod
    def validate_email_format(email: str) -> bool:
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email))

    @staticmethod
    def sanitize_display_name(name: str) -> str:
        return " ".join(name.strip().split())[:50] if name else ""
