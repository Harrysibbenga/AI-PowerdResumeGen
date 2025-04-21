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

        if settings.USE_DEEPSEEK and settings.DEEPSEEK_API_KEY:
            resume_content = await generate_resume_with_deepseek(request.profile.dict(), request.tone)
        else:
            resume_content = await generate_resume_with_gpt(request.profile.dict(), request.tone)

        resume_id = str(uuid.uuid4())
        resume_ref = db.collection("resumes").document(resume_id)

        resume_data = {
            "id": resume_id,
            "user_id": user_id,
            "industry": request.profile.industry,
            "profile_data": request.profile.dict(),
            "ai_content": resume_content,
            "export_status": "free",
            "created_at": datetime.now()
        }

        resume_ref.set(resume_data)

        return {
            "id": resume_id,
            "sections": resume_content,
            "message": "Resume generated successfully!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")

@router.get("/resumes/{resume_id}", response_model=Dict[str, Any])
async def get_resume(resume_id: str, user: Dict = Depends(get_current_user)):
    try:
        user_id = user["uid"]
        resume_ref = db.collection("resumes").document(resume_id)
        resume = resume_ref.get()

        if not resume.exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume_data = resume.to_dict()

        if resume_data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        return resume_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resume: {str(e)}")

@router.get("/resumes", response_model=List[Dict[str, Any]])
async def list_resumes(user: Dict = Depends(get_current_user)):
    try:
        user_id = user["uid"]
        resumes_ref = db.collection("resumes").where("user_id", "==", user_id)
        resumes = resumes_ref.stream()
        return [resume.to_dict() for resume in resumes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing resumes: {str(e)}")

@router.post("/export", response_model=ExportResponse)
async def export_resume(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(get_current_user)
):
    try:
        user_id = user["uid"]
        resume_ref = db.collection("resumes").document(request.resumeId)
        resume = resume_ref.get()

        if not resume.exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume_data = resume.to_dict()

        if resume_data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized export attempt")

        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        is_subscribed = user_doc.exists and user_doc.to_dict().get("subscription", False)

        if not is_subscribed and resume_data["export_status"] not in ["paid", "subscribed"]:
            return {"download_url": "", "message": "payment_required"}

        if request.format.lower() == "pdf":
            export_path = f"exports/{user_id}/{request.resumeId}.pdf"
            background_tasks.add_task(export_to_pdf, resume_data, request.content, export_path)
        elif request.format.lower() == "docx":
            export_path = f"exports/{user_id}/{request.resumeId}.docx"
            background_tasks.add_task(export_to_docx, resume_data, request.content, export_path)
        else:
            raise HTTPException(status_code=400, detail="Invalid export format")

        resume_ref.update({"export_status": "subscribed" if is_subscribed else "paid"})
        return {"download_url": f"/api/v1/download/{export_path}", "message": "Export successful"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting resume: {str(e)}")

@router.get("/download/{user_id}/{file_name}")
async def download_file(user_id: str, file_name: str, user: Dict = Depends(get_current_user)):
    pass
