import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",  # This will run the FastAPI instance from main.py
        host="0.0.0.0",
        port=8000,
        reload=not settings.is_production,
        log_level="debug" if not settings.is_production else "info",
    )