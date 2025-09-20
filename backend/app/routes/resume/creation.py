from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from app.dependencies.auth_dependencies import get_current_user
from app.services.gpt_service import generate_resume_with_gpt
from app.services.deepseek_service import generate_resume_with_deepseek
from app.core.config import settings
from app.core.firebase import db
from app.models.resume import (
    ResumeRequest,
    ResumeResponse,
    ExportStatus
)
from app.helpers.resume_helpers import (
    generate_summary_excerpt,
    count_resume_sections,
    estimate_word_count
)
import uuid
from datetime import datetime
from app.core.error import LoggedHTTPException

router = APIRouter()

@router.post("/", response_model=ResumeResponse)
async def create_resume(request: ResumeRequest, user: Dict = Depends(get_current_user)):
    try:
        user_id = user["uid"]

        if not request.profile_data.work_experience and not request.profile_data.education:
            raise LoggedHTTPException(
                status_code=400,
                detail="At least one work experience or education entry is required"
            )

        generator = generate_resume_with_deepseek if settings.USE_DEEPSEEK and settings.DEEPSEEK_API_KEY else generate_resume_with_gpt
        resume_content = await generator(
            profile_data=request.profile_data.dict(),
            tone=request.ai_tone.value,
            industry=request.industry,
            target_job_title=request.target_job_title,
            target_job_role=request.target_job_role,
            focus_keywords=request.focus_keywords,
            template_id=request.template_id.value
        )

        resume_id = str(uuid.uuid4())
        summary_excerpt = generate_summary_excerpt(resume_content)
        now = datetime.now()

        resume_data = {
            "id": resume_id,
            "user_id": user_id,
            "title": request.title,
            "target_job_title": request.target_job_title,
            "target_job_role": request.target_job_role,
            "target_company": request.target_company,
            "industry": request.industry,
            "template_id": request.template_id.value,
            "tone": request.ai_tone.value,
            "length": request.ai_length.value,
            "focus_keywords": request.focus_keywords,
            "use_ai": request.use_ai,
            "include_projects": request.include_projects,
            "include_certifications": request.include_certifications,
            "include_languages": request.include_languages,
            "profile_data": request.profile_data.dict(),
            "ai_content": resume_content,
            "summary_excerpt": summary_excerpt,
            "sections_count": count_resume_sections(resume_content),
            "word_count": estimate_word_count(resume_content),
            "export_status": ExportStatus.FREE.value,
            "created_at": now,
            "updated_at": now,
            "version": 1
        }

        if request.custom_sections:
            resume_data["custom_sections"] = request.custom_sections

        db.collection("resumes").document(resume_id).set(resume_data)

        return ResumeResponse(
            id=resume_id,
            title=request.title,
            target_job_title=request.target_job_title,
            target_job_role=request.target_job_role,
            sections=resume_content,
            message="Resume generated successfully!",
            created_at=now,
            summary_excerpt=summary_excerpt,
            industry=request.industry,
            template_id=request.template_id,
            export_status=ExportStatus.FREE
        )

    except HTTPException:
        raise
    except Exception as e:
        raise LoggedHTTPException(status_code=500, detail=f"Error generating resume: {str(e)}", exc=e)


@router.post("/{resume_id}/duplicate", response_model=ResumeResponse)
async def duplicate_resume(resume_id: str, user: Dict = Depends(get_current_user)):
    try:
        user_id = user["uid"]
        original = db.collection("resumes").document(resume_id).get()

        if not original.exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        data = original.to_dict()
        if data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        new_id = str(uuid.uuid4())
        now = datetime.now()

        data.update({
            "id": new_id,
            "title": f"{data['title']} (Copy)",
            "created_at": now,
            "updated_at": now,
            "version": 1,
            "export_status": ExportStatus.FREE.value
        })
        data.pop("deleted_at", None)

        db.collection("resumes").document(new_id).set(data)

        return ResumeResponse(
            id=new_id,
            title=data["title"],
            target_job_title=data["target_job_title"],
            target_job_role=data.get("target_job_role"),
            sections=data["ai_content"],
            profile_data=data.get("profile_data"),
            message="Resume duplicated successfully!",
            created_at=data["created_at"],
            updated_at=data.get("updated_at"),
            summary_excerpt=data.get("summary_excerpt"),
            industry=data["industry"],
            template_id=data["template_id"],
            export_status=data.get("export_status", ExportStatus.FREE.value),
            version=data.get("version", 1),
            sections_count=data.get("sections_count"),
            word_count=data.get("word_count")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise LoggedHTTPException(status_code=500, detail=f"Error duplicating resume: {str(e)}", exc=e)


@router.post("/{resume_id}/regenerate", response_model=ResumeResponse)
async def regenerate_resume_content(resume_id: str, user: Dict = Depends(get_current_user)):
    try:
        user_id = user["uid"]
        doc = db.collection("resumes").document(resume_id).get()

        if not doc.exists:
            raise LoggedHTTPException(status_code=404, detail="Resume not found")

        data = doc.to_dict()

        if data["user_id"] != user_id:
            raise LoggedHTTPException(status_code=403, detail="Unauthorized access")

        generator = generate_resume_with_deepseek if settings.USE_DEEPSEEK and settings.DEEPSEEK_API_KEY else generate_resume_with_gpt
        new_content = await generator(
            profile_data=data["profile_data"],
            tone=data["tone"],
            industry=data['industry'],
            target_job_title=data["target_job_title"],
            target_job_role=data.get("target_job_role"),
            focus_keywords=data.get("focus_keywords"),
            template_id=data["template_id"]
        )

        now = datetime.now()
        updates = {
            "ai_content": new_content,
            "summary_excerpt": generate_summary_excerpt(new_content),
            "sections_count": count_resume_sections(new_content),
            "word_count": estimate_word_count(new_content),
            "version": data.get("version", 1) + 1,
            "updated_at": now
        }

        db.collection("resumes").document(resume_id).update(updates)
        updated = db.collection("resumes").document(resume_id).get().to_dict()

        return ResumeResponse(
            id=updated["id"],
            title=updated["title"],
            target_job_title=updated["target_job_title"],
            target_job_role=updated.get("target_job_role"),
            sections=updated["ai_content"],
            profile_data=updated.get("profile_data"),
            message="Resume content regenerated successfully!",
            created_at=updated["created_at"],
            updated_at=updated.get("updated_at"),
            summary_excerpt=updated.get("summary_excerpt"),
            industry=updated["industry"],
            template_id=updated["template_id"],
            export_status=updated.get("export_status", ExportStatus.FREE.value),
            version=updated.get("version", 1),
            sections_count=updated.get("sections_count"),
            word_count=updated.get("word_count")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise LoggedHTTPException(status_code=500, detail=f"Error regenerating resume content: {str(e)}", exc=e)
