from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import firebase_admin
from firebase_admin import firestore
from app.api.v1.auth import get_current_user
from app.services.gpt_service import generate_resume_with_gpt
from app.services.deepseek_service import generate_resume_with_deepseek
from app.services.export_service import export_to_pdf, export_to_docx
from app.core.config import settings
import uuid
from datetime import datetime

router = APIRouter()
db = firestore.client()

# Models
class Experience(BaseModel):
    title: str
    company: str
    startDate: str
    endDate: Optional[str] = None
    current: bool = False
    description: str

class Education(BaseModel):
    degree: str
    institution: str
    startYear: int
    endYear: Optional[int] = None

class UserProfile(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    experience: List[Experience]
    education: List[Education]
    skills: List[str]
    industry: str

class ResumeRequest(BaseModel):
    profile: UserProfile
    tone: Optional[str] = "professional"
    length: Optional[str] = "standard"

class ResumeResponse(BaseModel):
    id: str
    sections: Dict[str, Any]
    message: str

class ExportRequest(BaseModel):
    resumeId: str
    format: str  # "pdf" or "docx"
    content: Dict[str, Any]

class ExportResponse(BaseModel):
    download_url: str
    message: str

# Endpoints
@router.post("/resumes", response_model=ResumeResponse)
async def create_resume(
    request: ResumeRequest,
    user: Dict = Depends(get_current_user)
):
    try:
        user_id = user["uid"]
        
        # Choose AI service based on settings
        if settings.USE_DEEPSEEK and settings.DEEPSEEK_API_KEY:
            resume_content = await generate_resume_with_deepseek(request.profile.dict(), request.tone)
        else:
            resume_content = await generate_resume_with_gpt(request.profile.dict(), request.tone)
        
        # Create resume document in Firestore
        resume_id = str(uuid.uuid4())
        resume_ref = db.collection("resumes").document(resume_id)
        
        resume_data = {
            "id": resume_id,
            "user_id": user_id,
            "industry": request.profile.industry,
            "profile_data": request.profile.dict(),
            "ai_content": resume_content,
            "export_status": "free",  # Not downloaded yet
            "created_at": datetime.now()
        }
        
        resume_ref.set(resume_data)
        
        return {
            "id": resume_id,
            "sections": resume_content,
            "message": "Resume generated successfully!"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating resume: {str(e)}"
        )

@router.get("/resumes/{resume_id}", response_model=Dict[str, Any])
async def get_resume(
    resume_id: str,
    user: Dict = Depends(get_current_user)
):
    try:
        user_id = user["uid"]
        
        # Get resume from Firestore
        resume_ref = db.collection("resumes").document(resume_id)
        resume = resume_ref.get()
        
        if not resume.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        resume_data = resume.to_dict()
        
        # Verify ownership
        if resume_data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resume"
            )
        
        return resume_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resume: {str(e)}"
        )

@router.get("/resumes", response_model=List[Dict[str, Any]])
async def list_resumes(
    user: Dict = Depends(get_current_user)
):
    try:
        user_id = user["uid"]
        
        # Query resumes for the current user
        resumes_ref = db.collection("resumes").where("user_id", "==", user_id).order_by("created_at", direction=firestore.Query.DESCENDING)
        resumes = resumes_ref.stream()
        
        return [resume.to_dict() for resume in resumes]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing resumes: {str(e)}"
        )

@router.post("/export", response_model=ExportResponse)
async def export_resume(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(get_current_user)
):
    try:
        user_id = user["uid"]
        
        # Get resume from Firestore
        resume_ref = db.collection("resumes").document(request.resumeId)
        resume = resume_ref.get()
        
        if not resume.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        resume_data = resume.to_dict()
        
        # Verify ownership
        if resume_data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to export this resume"
            )
        
        # Check subscription status
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            is_subscribed = False
        else:
            user_data = user_doc.to_dict()
            is_subscribed = user_data.get("subscription", False)
        
        # If not subscribed and already exported, require payment
        if not is_subscribed and resume_data["export_status"] not in ["paid", "subscribed"]:
            # Client should handle payment flow
            return {
                "download_url": "",
                "message": "payment_required"
            }
        
        # Generate PDF or DOCX
        if request.format.lower() == "pdf":
            export_path = f"exports/{user_id}/{request.resumeId}.pdf"
            background_tasks.add_task(
                export_to_pdf,
                resume_data,
                request.content,
                export_path
            )
        elif request.format.lower() == "docx":
            export_path = f"exports/{user_id}/{request.resumeId}.docx"
            background_tasks.add_task(
                export_to_docx,
                resume_data,
                request.content,
                export_path
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid export format. Supported formats: pdf, docx"
            )
        
        # Update export status
        resume_ref.update({
            "export_status": "subscribed" if is_subscribed else "paid"
        })
        
        # Return download URL
        download_url = f"/api/v1/download/{export_path}"
        
        return {
            "download_url": download_url,
            "message": "Export successful"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting resume: {str(e)}"
        )

@router.get("/download/{user_id}/{file_name}")
async def download_file(
    user_id: str,
    file_name: str,
    user: Dict = Depends(get_current_user)
):
    # Implementation for file download
    pass