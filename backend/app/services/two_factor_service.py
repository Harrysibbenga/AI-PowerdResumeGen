"""
Two-Factor Authentication service using TOTP
"""
import pyotp
import qrcode
from io import BytesIO
import base64
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TwoFactorService:
    """Service class for handling 2FA operations"""
    
    def __init__(self, app_name: str = "Your App"):
        self.app_name = app_name
    
    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret
        
        Returns:
            str: Base32 encoded secret
        """
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, user_email: str) -> Dict[str, str]:
        """
        Generate QR code for 2FA setup
        
        Args:
            secret: TOTP secret
            user_email: User's email address
            
        Returns:
            Dict containing QR code data and secret
        """
        try:
            # Create TOTP instance
            totp = pyotp.TOTP(secret)
            
            # Generate provisioning URI
            provisioning_uri = totp.provisioning_uri(
                name=user_email,
                issuer_name=self.app_name
            )
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "qr_code": f"data:image/png;base64,{img_str}",
                "secret": secret,
                "manual_entry_key": self._format_secret_for_manual_entry(secret)
            }
            
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            raise
    
    def verify_code(self, secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Verify TOTP code
        
        Args:
            secret: TOTP secret
            code: Code to verify
            valid_window: Number of time windows to check (default: 1)
            
        Returns:
            bool: True if code is valid
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=valid_window)
        except Exception as e:
            logger.error(f"Error verifying 2FA code: {str(e)}")
            return False
    
    def get_current_code(self, secret: str) -> str:
        """
        Get current TOTP code (for testing purposes)
        
        Args:
            secret: TOTP secret
            
        Returns:
            str: Current TOTP code
        """
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    def _format_secret_for_manual_entry(self, secret: str) -> str:
        """
        Format secret for manual entry in authenticator apps
        
        Args:
            secret: Base32 secret
            
        Returns:
            str: Formatted secret with spaces for readability
        """
        # Add spaces every 4 characters for readability
        return ' '.join([secret[i:i+4] for i in range(0, len(secret), 4)])
    
    def generate_backup_codes(self, count: int = 8) -> list:
        """
        Generate backup codes for 2FA recovery
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            list: List of backup codes
        """
        import secrets
        import string
        
        codes = []
        for _ in range(count):
            # Generate 8-character backup code
            code = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
            # Format as XXXX-XXXX for readability
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        
        return codes
    
    def validate_backup_code(self, stored_codes: list, provided_code: str, use_once: bool = True) -> Dict[str, Any]:
        """
        Validate backup code
        
        Args:
            stored_codes: List of valid backup codes
            provided_code: Code provided by user
            use_once: Whether to remove code after successful validation
            
        Returns:
            Dict with validation result and updated codes
        """
        # Normalize the provided code (remove spaces, convert to lowercase)
        normalized_code = provided_code.replace(" ", "").replace("-", "").lower()
        
        for i, stored_code in enumerate(stored_codes):
            # Normalize stored code for comparison
            normalized_stored = stored_code.replace("-", "").lower()
            
            if normalized_code == normalized_stored:
                if use_once:
                    # Remove the used code
                    updated_codes = stored_codes.copy()
                    updated_codes.pop(i)
                    return {
                        "valid": True,
                        "updated_codes": updated_codes,
                        "codes_remaining": len(updated_codes)
                    }
                else:
                    return {
                        "valid": True,
                        "updated_codes": stored_codes,
                        "codes_remaining": len(stored_codes)
                    }
        
        return {
            "valid": False,
            "updated_codes": stored_codes,
            "codes_remaining": len(stored_codes)
        }

# Create singleton instance
two_factor_service = TwoFactorService()