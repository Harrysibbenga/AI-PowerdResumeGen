from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import your existing routers
from app.api.v1 import resume, payments

# Import the new refactored auth router
from app.routers import auth

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("Starting up Resume Generator API...")
    logger.info(f"Environment: {getattr(settings, 'ENVIRONMENT', 'development')}")
    logger.info(f"Firebase configured: {'Yes' if settings.FIREBASE_SERVICE_ACCOUNT_PATH else 'No'}")
    logger.info(f"SMTP configured: {'Yes' if settings.SMTP_USERNAME else 'No'}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Resume Generator API...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered resume generator API with advanced authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
# Note: Updated auth router with new structure
app.include_router(
    auth.router, 
    prefix="/api/v1/auth", 
    tags=["authentication"]
)

app.include_router(
    resume.router, 
    prefix="/api/v1", 
    tags=["resume"]
)

app.include_router(
    payments.router, 
    prefix="/api/v1", 
    tags=["payments"]
)

# Health check endpoint with enhanced information
@app.get("/", tags=["health"])
def health_check():
    """Enhanced health check with service status"""
    return {
        "status": "ok", 
        "message": "Resume Generator API is running",
        "version": "1.0.0",
        "services": {
            "authentication": "enabled",
            "resume_generation": "enabled",
            "payments": "enabled",
            "email_service": "configured" if settings.SMTP_USERNAME else "not_configured",
            "firebase": "configured" if settings.FIREBASE_SERVICE_ACCOUNT_PATH else "not_configured"
        }
    }

# Additional health check for authentication service
@app.get("/api/v1/auth/health", tags=["health"])
def auth_health_check():
    """Specific health check for authentication service"""
    return {
        "service": "authentication",
        "status": "healthy",
        "features": {
            "user_management": True,
            "email_verification": bool(settings.SMTP_USERNAME),
            "two_factor_auth": True,
            "session_management": True,
            "password_reset": bool(settings.SMTP_USERNAME)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )