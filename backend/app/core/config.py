import os
from typing import List, Optional
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "Resume Generator API"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:4321"]
    
    # Authentication settings
    FIREBASE_SERVICE_ACCOUNT_PATH: Optional[str] = None
    FIREBASE_WEB_API_KEY: str = os.getenv("FIREBASE_WEB_API_KEY", "")
    
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
    EXPORT_TEMPLATES_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
    
    @validator("FIREBASE_SERVICE_ACCOUNT_PATH", pre=True)
    def set_firebase_service_account_path(cls, v):
        if not v:
            # If not provided, use default location
            return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "firebase", "serviceAccount.json")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings object
settings = Settings()