from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Dict, Optional
import firebase_admin
from firebase_admin import auth, firestore
from firebase_admin import credentials
import os
from app.core.config import settings

# Initialize Firebase Admin SDK (if not already initialized)
try:
    app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
    app = firebase_admin.initialize_app(cred)

router = APIRouter()
db = firestore.client()

# Models
class UserCreate(BaseModel):
    email: str
    password: str
    displayName: Optional[str] = None

class UserResponse(BaseModel):
    uid: str
    email: str
    displayName: Optional[str] = None
    isSubscribed: bool = False

# Helper function to verify Firebase ID token
async def get_current_user(request: Request):
    authorization = request.headers.get("Authorization")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    token = authorization.split("Bearer ")[1]
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}"
        )

# Endpoints
@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.displayName or ""
        )
        
        # Store user in Firestore
        user_ref = db.collection("users").document(user.uid)
        user_ref.set({
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name or "",
            "subscription": False,
            "stripe_id": "",
            "created_at": firestore.SERVER_TIMESTAMP
        })
        
        return {
            "uid": user.uid,
            "email": user.email,
            "displayName": user.display_name,
            "isSubscribed": False
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {str(e)}"
        )

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(user_data: Dict = Depends(get_current_user)):
    try:
        user_id = user_data["uid"]
        
        # Get user from Firestore to check subscription status
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            # If somehow user exists in Auth but not in Firestore, create it
            user = auth.get_user(user_id)
            
            user_ref.set({
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name or "",
                "subscription": False,
                "stripe_id": "",
                "created_at": firestore.SERVER_TIMESTAMP
            })
            
            return {
                "uid": user.uid,
                "email": user.email,
                "displayName": user.display_name,
                "isSubscribed": False
            }
        
        user_data = user_doc.to_dict()
        
        return {
            "uid": user_data["uid"],
            "email": user_data["email"],
            "displayName": user_data.get("display_name", ""),
            "isSubscribed": user_data.get("subscription", False)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profile: {str(e)}"
        )

@router.delete("/users/me")
async def delete_user(user_data: Dict = Depends(get_current_user)):
    try:
        user_id = user_data["uid"]
        
        # Delete user from Firebase Authentication
        auth.delete_user(user_id)
        
        # Delete user from Firestore
        db.collection("users").document(user_id).delete()
        
        return {"message": "User deleted successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )