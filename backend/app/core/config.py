import os
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import validator, Field

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "Resume Generator API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Frontend URL for email links and redirects
    FRONTEND_URL: str = Field(default="http://localhost:4321", env="FRONTEND_URL")
    
     # CORS settings - Fix the parsing issue
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=[FRONTEND_URL, "http://localhost:4321"],
        env="CORS_ORIGINS"
    )
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS_REMEMBER: int = 30  # 30 days for remember me
    
    # Account Lockout Settings
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 30
    
    # Authentication settings
    FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "")
    FIREBASE_WEB_API_KEY: str = os.getenv("FIREBASE_WEB_API_KEY", "")
    
    # Session Management
    SESSION_TIMEOUT_HOURS: int = Field(default=24, env="SESSION_TIMEOUT_HOURS")
    
    # SMTP Email Configuration
    SMTP_SERVER: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_FROM_EMAIL: str = Field(default="", env="SMTP_FROM_EMAIL")
    SMTP_FROM_NAME: str = Field(default="Resume Generator", env="SMTP_FROM_NAME")
    
    # Email Template Settings
    EMAIL_TEMPLATES_DIR: str = Field(
        default_factory=lambda: os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "templates", "email"
        ),
        env="EMAIL_TEMPLATES_DIR"
    )
    
    # Security Settings
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    TOKEN_EXPIRY_HOURS: int = Field(default=24, env="TOKEN_EXPIRY_HOURS")
    RESET_TOKEN_EXPIRY_HOURS: int = Field(default=1, env="RESET_TOKEN_EXPIRY_HOURS")
    
    # Rate Limiting Settings
    RATE_LIMIT_AUTH_REQUESTS: int = Field(default=5, env="RATE_LIMIT_AUTH_REQUESTS")
    RATE_LIMIT_AUTH_WINDOW: int = Field(default=60, env="RATE_LIMIT_AUTH_WINDOW")  # seconds
    RATE_LIMIT_EMAIL_REQUESTS: int = Field(default=3, env="RATE_LIMIT_EMAIL_REQUESTS")
    RATE_LIMIT_EMAIL_WINDOW: int = Field(default=300, env="RATE_LIMIT_EMAIL_WINDOW")  # seconds
    RATE_LIMIT_2FA_REQUESTS: int = Field(default=5, env="RATE_LIMIT_2FA_REQUESTS")
    RATE_LIMIT_2FA_WINDOW: int = Field(default=300, env="RATE_LIMIT_2FA_WINDOW")  # seconds
    
    # Two-Factor Authentication Settings
    APP_NAME_2FA: str = Field(default="Resume Generator", env="APP_NAME_2FA")
    TOTP_VALID_WINDOW: int = Field(default=1, env="TOTP_VALID_WINDOW")  # Number of time windows to accept
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GPT_MODEL: str = "gpt-4-turbo"
    
    # DeepSeek settings
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_MODEL: str = "deepseek-coder"
    USE_DEEPSEEK: bool = False  # Default to OpenAI
    
    # Stripe settings
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_ONE_TIME_PRICE_ID: str = os.getenv("STRIPE_ONE_TIME_PRICE_ID", "")
    STRIPE_SUBSCRIPTION_PRICE_ID: str = os.getenv("STRIPE_SUBSCRIPTION_PRICE_ID", "")
    
    # Export settings
    EXPORT_TEMPLATES_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "templates"
    )
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Database/Storage Settings (for future use)
    CLEANUP_EXPIRED_TOKENS_HOURS: int = Field(default=6, env="CLEANUP_EXPIRED_TOKENS_HOURS")
    
    @validator("FIREBASE_SERVICE_ACCOUNT_PATH", pre=True)
    def set_firebase_service_account_path(cls, v):
        if not v:
            # If not provided, use default location
            return os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "firebase", "serviceAccount.json"
            )
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """
        Parse CORS_ORIGINS from string or list
        Handles: "url1,url2,url3" or ["url1", "url2", "url3"]
        """
        if isinstance(v, str):
            # Handle comma-separated string
            if ',' in v:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
            else:
                # Single URL as string
                return [v.strip()] if v.strip() else ["http://localhost:3000"]
        elif isinstance(v, list):
            # Already a list
            return [str(origin).strip() for origin in v if str(origin).strip()]
        else:
            # Fallback to default
            return ["http://localhost:3000", "http://localhost:4321"]
    
    @validator("SMTP_FROM_EMAIL")
    def validate_smtp_from_email(cls, v, values):
        """Set SMTP_FROM_EMAIL to SMTP_USERNAME if not provided"""
        if not v and values.get("SMTP_USERNAME"):
            return values["SMTP_USERNAME"]
        return v
    
    @validator("EMAIL_TEMPLATES_DIR")
    def validate_email_templates_dir(cls, v):
        """Ensure email templates directory exists"""
        if not os.path.exists(v):
            try:
                os.makedirs(v, exist_ok=True)
            except Exception:
                pass  # Use default templates if directory creation fails
        return v
    
    # Computed properties
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_email_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.SMTP_USERNAME and self.SMTP_PASSWORD and self.SMTP_FROM_EMAIL)
    
    @property
    def is_firebase_configured(self) -> bool:
        """Check if Firebase is properly configured"""
        return bool(self.FIREBASE_SERVICE_ACCOUNT_PATH and os.path.exists(self.FIREBASE_SERVICE_ACCOUNT_PATH))
    
    @property
    def is_stripe_configured(self) -> bool:
        """Check if Stripe is properly configured"""
        return bool(self.STRIPE_API_KEY and self.STRIPE_WEBHOOK_SECRET)
    
    @property
    def email_service_config(self) -> dict:
        """Get email service configuration dictionary"""
        return {
            "server": self.SMTP_SERVER,
            "port": self.SMTP_PORT,
            "username": self.SMTP_USERNAME,
            "password": self.SMTP_PASSWORD,
            "from_email": self.SMTP_FROM_EMAIL,
            "from_name": self.SMTP_FROM_NAME,
        }
    
    @property
    def rate_limit_config(self) -> dict:
        """Get rate limiting configuration"""
        return {
            "auth": {
                "requests": self.RATE_LIMIT_AUTH_REQUESTS,
                "window": self.RATE_LIMIT_AUTH_WINDOW
            },
            "email": {
                "requests": self.RATE_LIMIT_EMAIL_REQUESTS,
                "window": self.RATE_LIMIT_EMAIL_WINDOW
            },
            "2fa": {
                "requests": self.RATE_LIMIT_2FA_REQUESTS,
                "window": self.RATE_LIMIT_2FA_WINDOW
            }
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore" 
        # Allow arbitrary types for computed properties
        arbitrary_types_allowed = True

# Create global settings object
settings = Settings()

# Validation on startup
def validate_critical_settings():
    """Validate critical settings and provide helpful error messages"""
    errors = []
    warnings = []
    
    if not settings.is_firebase_configured:
        errors.append(
            f"Firebase not configured. Please set FIREBASE_SERVICE_ACCOUNT_PATH "
            f"or place serviceAccount.json at {settings.FIREBASE_SERVICE_ACCOUNT_PATH}"
        )
    
    if not settings.OPENAI_API_KEY and not settings.DEEPSEEK_API_KEY:
        errors.append("No AI service configured. Please set OPENAI_API_KEY or DEEPSEEK_API_KEY")
    
    if settings.is_production and not settings.is_email_configured:
        errors.append(
            "Email service not configured for production. "
            "Please set SMTP_USERNAME, SMTP_PASSWORD, and SMTP_FROM_EMAIL"
        )
    
    if not settings.is_email_configured:
        warnings.append(
            "Email service not configured. "
            "Password reset and email verification features will not work."
        )
    
    # Print results
    if errors or warnings:
        print("⚠️  Configuration Status:")
        
        if errors:
            print("❌ Errors (will prevent startup):")
            for error in errors:
                print(f"   - {error}")
        
        if warnings:
            print("⚠️  Warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        print(f"✅ Firebase: {'Configured' if settings.is_firebase_configured else 'Not configured'}")
        print(f"✅ Email: {'Configured' if settings.is_email_configured else 'Not configured'}")
        print(f"✅ CORS Origins: {settings.CORS_ORIGINS}")
        print()
    
    if errors and settings.is_production:
        raise ValueError("Critical configuration errors detected. Please fix before starting.")

# Run validation
validate_critical_settings()