# app/core/firebase.py

import firebase_admin
from firebase_admin import firestore, credentials, auth
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

def initialize_firebase():
    """
    Initialize Firebase app with proper error handling and singleton pattern
    """
    try:
        # Check if Firebase is already initialized (singleton pattern)
        try:
            app = firebase_admin.get_app()
            logger.info("Firebase already initialized, reusing existing app")
            return app
        except ValueError:
            # Firebase not initialized yet, proceed with initialization
            logger.info("Initializing Firebase for the first time")
            pass
        
        # Validate service account path
        if not settings.FIREBASE_SERVICE_ACCOUNT_PATH:
            raise ValueError("FIREBASE_SERVICE_ACCOUNT_PATH not configured")
        
        # Convert to absolute path and check if file exists
        service_account_path = os.path.abspath(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        
        if not os.path.exists(service_account_path):
            raise FileNotFoundError(f"Firebase service account file not found: {service_account_path}")
        
        # Initialize Firebase with credentials
        cred = credentials.Certificate(service_account_path)
        app = firebase_admin.initialize_app(cred)
        
        logger.info(f"Firebase initialized successfully with project: {app.project_id}")
        return app
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        raise

# Initialize Firebase app (singleton)
firebase_app = initialize_firebase()

# Export firestore db client and auth
db = firestore.client(firebase_app)
firebase_auth = auth

# Export commonly used Firestore utilities
SERVER_TIMESTAMP = firestore.SERVER_TIMESTAMP
DELETE_FIELD = firestore.DELETE_FIELD

# Optional: Add a function to check Firebase health
def check_firebase_health():
    """
    Check if Firebase services are working properly
    
    Returns:
        dict: Status of Firebase services
    """
    try:
        status = {
            "firebase_initialized": firebase_app is not None,
            "project_id": firebase_app.project_id if firebase_app else None,
            "firestore_available": False,
            "auth_available": False
        }
        
        # Test Firestore
        try:
            # Try a simple Firestore operation
            db.collection('_health_check').limit(1).get()
            status["firestore_available"] = True
        except Exception as e:
            logger.warning(f"Firestore health check failed: {e}")
        
        # Test Auth
        try:
            # Try a simple Auth operation
            firebase_auth.list_users(max_results=1)
            status["auth_available"] = True
        except Exception as e:
            logger.warning(f"Auth health check failed: {e}")
        
        return status
        
    except Exception as e:
        logger.error(f"Firebase health check failed: {e}")
        return {"error": str(e), "firebase_initialized": False}

# Log initialization status
try:
    health_status = check_firebase_health()
    logger.info(f"Firebase health check: {health_status}")
except Exception as e:
    logger.error(f"Firebase health check failed: {e}")