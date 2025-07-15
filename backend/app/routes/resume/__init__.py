from fastapi import APIRouter
from .creation import router as creation_router
from .management import router as management_router
from .export import router as export_router
from .analytics import router as analytics_router

# Create main resume router
router = APIRouter()

# Include sub-routers with appropriate prefixes
router.include_router(creation_router, prefix="", tags=["resume-creation"])
router.include_router(management_router, prefix="", tags=["resume-management"])
router.include_router(export_router, prefix="/export", tags=["resume-export"])
router.include_router(analytics_router, prefix="/analytics", tags=["resume-analytics"])