"""
Email service for sending authentication-related emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service class for handling email operations"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
    
    async def send_email(self, to_email: str, subject: str, body: str, is_html: bool = True) -> bool:
        """
        Send email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body content is HTML
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            body_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, body_type))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    async def send_verification_email(self, to_email: str, display_name: str, token: str) -> bool:
        """
        Send email verification email
        
        Args:
            to_email: User's email address
            display_name: User's display name
            token: Verification token
            
        Returns:
            bool: True if email sent successfully
        """
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        subject = "Verify Your Email Address"
        body = self._get_verification_email_template(display_name, verification_link)
        
        return await self.send_email(to_email, subject, body)
    
    async def send_password_reset_email(self, to_email: str, display_name: str, token: str) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: User's email address
            display_name: User's display name
            token: Reset token
            
        Returns:
            bool: True if email sent successfully
        """
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        subject = "Password Reset Request"
        body = self._get_password_reset_email_template(display_name, reset_link)
        
        return await self.send_email(to_email, subject, body)
    
    async def send_password_changed_notification(self, to_email: str, display_name: str) -> bool:
        """
        Send password change notification email
        
        Args:
            to_email: User's email address
            display_name: User's display name
            
        Returns:
            bool: True if email sent successfully
        """
        subject = "Password Changed Successfully"
        body = self._get_password_changed_email_template(display_name)
        
        return await self.send_email(to_email, subject, body)
    
    async def send_2fa_enabled_notification(self, to_email: str, display_name: str) -> bool:
        """
        Send 2FA enabled notification email
        
        Args:
            to_email: User's email address
            display_name: User's display name
            
        Returns:
            bool: True if email sent successfully
        """
        subject = "Two-Factor Authentication Enabled"
        body = self._get_2fa_enabled_email_template(display_name)
        
        return await self.send_email(to_email, subject, body)
    
    async def send_2fa_disabled_notification(self, to_email: str, display_name: str) -> bool:
        """
        Send 2FA disabled notification email
        
        Args:
            to_email: User's email address
            display_name: User's display name
            
        Returns:
            bool: True if email sent successfully
        """
        subject = "Two-Factor Authentication Disabled"
        body = self._get_2fa_disabled_email_template(display_name)
        
        return await self.send_email(to_email, subject, body)
    
    async def send_welcome_email(self, to_email: str, display_name: str) -> bool:
        """
        Send welcome email after email verification
        
        Args:
            to_email: User's email address
            display_name: User's display name
            
        Returns:
            bool: True if email sent successfully
        """
        subject = "Welcome to Our App!"
        body = self._get_welcome_email_template(display_name)
        
        return await self.send_email(to_email, subject, body)
    
    def _get_verification_email_template(self, display_name: str, verification_link: str) -> str:
        """Get HTML template for email verification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Email</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; text-align: center; margin-bottom: 30px;">Welcome{f", {display_name}" if display_name else ""}!</h2>
                
                <p style="color: #666; font-size: 16px;">Thank you for creating an account with us. To complete your registration, please verify your email address by clicking the button below:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Verify Email Address</a>
                </div>
                
                <p style="color: #666; font-size: 14px;">If the button doesn't work, you can also copy and paste this link into your browser:</p>
                <p style="color: #007bff; word-break: break-all; font-size: 14px;">{verification_link}</p>
                
                <p style="color: #666; font-size: 14px; margin-top: 30px;">This verification link will expire in 24 hours for security reasons.</p>
                
                <p style="color: #666; font-size: 14px;">If you didn't create an account with us, please ignore this email.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">This is an automated message, please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_password_reset_email_template(self, display_name: str, reset_link: str) -> str:
        """Get HTML template for password reset"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; text-align: center; margin-bottom: 30px;">Password Reset Request</h2>
                
                <p style="color: #666; font-size: 16px;">Hello{f" {display_name}" if display_name else ""},</p>
                
                <p style="color: #666; font-size: 16px;">We received a request to reset your password. Click the button below to create a new password:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background-color: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Reset Password</a>
                </div>
                
                <p style="color: #666; font-size: 14px;">If the button doesn't work, you can also copy and paste this link into your browser:</p>
                <p style="color: #dc3545; word-break: break-all; font-size: 14px;">{reset_link}</p>
                
                <p style="color: #666; font-size: 14px; margin-top: 30px;">This reset link will expire in 1 hour for security reasons.</p>
                
                <p style="color: #666; font-size: 14px;"><strong>If you didn't request this password reset, please ignore this email.</strong> Your password will remain unchanged.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">This is an automated message, please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_password_changed_email_template(self, display_name: str) -> str:
        """Get HTML template for password change notification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Changed</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; text-align: center; margin-bottom: 30px;">Password Changed Successfully</h2>
                
                <p style="color: #666; font-size: 16px;">Hello{f" {display_name}" if display_name else ""},</p>
                
                <p style="color: #666; font-size: 16px;">This email confirms that your password has been successfully changed.</p>
                
                <div style="background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>✓ Your password was changed successfully</strong>
                    <br>
                    <small>Changed on: {self._get_current_datetime()}</small>
                </div>
                
                <p style="color: #666; font-size: 14px;">If you didn't make this change, please contact our support team immediately.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">This is an automated message, please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_2fa_enabled_email_template(self, display_name: str) -> str:
        """Get HTML template for 2FA enabled notification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Two-Factor Authentication Enabled</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; text-align: center; margin-bottom: 30px;">🔐 Two-Factor Authentication Enabled</h2>
                
                <p style="color: #666; font-size: 16px;">Hello{f" {display_name}" if display_name else ""},</p>
                
                <p style="color: #666; font-size: 16px;">Two-factor authentication has been successfully enabled on your account. Your account is now more secure!</p>
                
                <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>🛡️ Enhanced Security Active</strong>
                    <br>
                    <small>You'll now need your authenticator app code when signing in.</small>
                </div>
                
                <p style="color: #666; font-size: 14px;">If you didn't enable two-factor authentication, please contact our support team immediately.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">This is an automated message, please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_2fa_disabled_email_template(self, display_name: str) -> str:
        """Get HTML template for 2FA disabled notification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Two-Factor Authentication Disabled</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; text-align: center; margin-bottom: 30px;">🔓 Two-Factor Authentication Disabled</h2>
                
                <p style="color: #666; font-size: 16px;">Hello{f" {display_name}" if display_name else ""},</p>
                
                <p style="color: #666; font-size: 16px;">Two-factor authentication has been disabled on your account.</p>
                
                <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>⚠️ Security Level Reduced</strong>
                    <br>
                    <small>Your account is now protected by password only.</small>
                </div>
                
                <p style="color: #666; font-size: 14px;">If you didn't disable two-factor authentication, please contact our support team immediately and consider re-enabling 2FA for better security.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">This is an automated message, please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_welcome_email_template(self, display_name: str) -> str:
        """Get HTML template for welcome email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Our App!</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; text-align: center; margin-bottom: 30px;">🎉 Welcome to Our App!</h2>
                
                <p style="color: #666; font-size: 16px;">Hello{f" {display_name}" if display_name else ""},</p>
                
                <p style="color: #666; font-size: 16px;">Congratulations! Your email has been verified and your account is now fully activated.</p>
                
                <div style="background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>✓ Account Successfully Activated</strong>
                    <br>
                    <small>You can now access all features of our platform.</small>
                </div>
                
                <h3 style="color: #333; margin-top: 30px;">Get Started:</h3>
                <ul style="color: #666; font-size: 14px;">
                    <li>Complete your profile setup</li>
                    <li>Enable two-factor authentication for extra security</li>
                    <li>Explore our features and settings</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/dashboard" style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Go to Dashboard</a>
                </div>
                
                <p style="color: #666; font-size: 14px;">If you have any questions, feel free to contact our support team.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">This is an automated message, please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_current_datetime(self) -> str:
        """Get current datetime as formatted string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

# Create singleton instance
email_service = EmailService()