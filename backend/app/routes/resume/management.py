from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Optional
from datetime import datetime

from app.dependencies.auth_dependencies import get_current_user
from app.services.gpt_service import generate_resume_with_gpt
from app.services.deepseek_service import generate_resume_with_deepseek
from app.core.config import settings
from app.core.firebase import db
from app.models.resume import (
    ResumeUpdateRequest,
    ResumeResponse,
    ResumeListItem,
    ResumeListResponse,
    ExportStatus
)
from app.helpers.resume_helpers import (
    generate_summary_excerpt,
    count_resume_sections,
    estimate_word_count
)

router = APIRouter()


@router.get("/{resume_id}", response_model=ResumeResponse)
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

        return ResumeResponse(
            id=resume_data["id"],
            title=resume_data["title"],
            target_job_title=resume_data["target_job_title"],
            target_job_role=resume_data.get("target_job_role"),
            target_company=resume_data.get("target_company"),
            sections=resume_data["ai_content"],
            profile_data=resume_data.get("profile_data"),
            created_at=resume_data["created_at"],
            updated_at=resume_data.get("updated_at"),
            summary_excerpt=resume_data.get("summary_excerpt"),
            industry=resume_data["industry"],
            template_id=resume_data["template_id"],
            export_status=resume_data.get("export_status", ExportStatus.FREE.value),
            version=resume_data.get("version", 1),
            sections_count=resume_data.get("sections_count"),
            word_count=resume_data.get("word_count")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resume: {str(e)}")


@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    user: Dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    industry: Optional[str] = None,
    template: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    try:
        user_id = user["uid"]
        query = db.collection("resumes").where("user_id", "==", user_id)

        if industry:
            query = query.where("industry", "==", industry)
        if template:
            query = query.where("template_id", "==", template)

        all_docs = list(query.stream())
        filtered_docs = []
        for doc in all_docs:
            data = doc.to_dict()
            if "deleted_at" in data:
                continue
            if search:
                search_text = f"{data.get('title', '')} {data.get('target_job_title', '')} {data.get('target_job_role', '')}".lower()
                if search.lower() not in search_text:
                    continue
            filtered_docs.append(data)

        total = len(filtered_docs)
        reverse_sort = sort_order == "desc"
        filtered_docs.sort(key=lambda x: x.get(sort_by, datetime.min), reverse=reverse_sort)

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_docs = filtered_docs[start_idx:end_idx]

        resumes = [ResumeListItem(
            id=d["id"],
            title=d["title"],
            target_job_title=d["target_job_title"],
            target_job_role=d.get("target_job_role"),
            target_company=d.get("target_company"),
            industry=d["industry"],
            template_id=d["template_id"],
            export_status=d.get("export_status", ExportStatus.FREE.value),
            created_at=d["created_at"],
            updated_at=d.get("updated_at"),
            summary_excerpt=d.get("summary_excerpt"),
            sections_count=d.get("sections_count", 0),
            word_count=d.get("word_count")
        ) for d in paginated_docs]

        return ResumeListResponse(
            resumes=resumes,
            total=total,
            page=page,
            per_page=per_page,
            has_next=end_idx < total,
            has_prev=page > 1
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing resumes: {str(e)}")


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: str,
    request: ResumeUpdateRequest,
    user: Dict = Depends(get_current_user)
):
    try:
        user_id = user["uid"]
        resume_ref = db.collection("resumes").document(resume_id)
        resume = resume_ref.get()

        if not resume.exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume_data = resume.to_dict()

        if resume_data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        updates = {"updated_at": datetime.now()}
        regenerate_content = request.use_ai

        if request.title:
            updates["title"] = request.title
        if request.target_job_title:
            updates["target_job_title"] = request.target_job_title
        if request.target_job_role:
            updates["target_job_role"] = request.target_job_role
        if request.target_company:
            updates["target_company"] = request.target_company
        if request.ai_tone:
            updates["ai_tone"] = request.ai_tone.value
        if request.ai_length:
            updates["ai_length"] = request.ai_length.value
        if request.template_id:
            updates["template_id"] = request.template_id.value
        if request.include_projects:
            updates["include_projects"] = request.include_projects
        if request.include_certifications:
            updates["include_certifications"] = request.include_certifications
        if request.include_languages:
            updates["include_languages"] = request.include_languages
        if request.focus_keywords:
            updates["focus_keywords"] = request.focus_keywords
        if request.custom_sections:
            updates["custom_sections"] = request.custom_sections

        if request.profile_data:
            profile_dict = request.profile_data.dict()
            updates["profile_data"] = profile_dict
            updates["industry"] = profile_dict.get("industry")
            updates["work_experience"] = profile_dict.get("work_experience")
            updates["education"] = profile_dict.get("education")
            updates["projects"] = profile_dict.get("projects")

        if regenerate_content:
            profile_data = request.profile_data.dict() if request.profile_data else resume_data.get("profile_data")
            tone = request.ai_tone.value if request.ai_tone else resume_data.get("ai_tone")
            target_job_title = request.target_job_title or resume_data.get("target_job_title")
            target_job_role = request.target_job_role or resume_data.get("target_job_role")
            focus_keywords = request.focus_keywords or resume_data.get("focus_keywords")
            template_id = request.template_id.value if request.template_id else resume_data.get("template_id")

            new_content = await generate_resume_with_deepseek(
                profile_data, tone, target_job_title, target_job_role, focus_keywords, template_id
            ) if settings.USE_DEEPSEEK and settings.DEEPSEEK_API_KEY else await generate_resume_with_gpt(
                profile_data, tone, target_job_title, target_job_role, focus_keywords, template_id
            )

            updates["ai_content"] = new_content
            updates["summary_excerpt"] = generate_summary_excerpt(new_content)
            updates["sections_count"] = count_resume_sections(new_content)
            updates["word_count"] = estimate_word_count(new_content)
            updates["version"] = resume_data.get("version", 1) + 1

        resume_ref.update(updates)
        updated_resume = resume_ref.get().to_dict()

        return ResumeResponse(
            id=updated_resume["id"],
            title=updated_resume["title"],
            target_job_title=updated_resume["target_job_title"],
            target_job_role=updated_resume.get("target_job_role"),
            target_company=updated_resume.get("target_company"),
            sections=updated_resume["ai_content"],
            profile_data=updated_resume.get("profile_data"),
            created_at=updated_resume["created_at"],
            updated_at=updated_resume.get("updated_at"),
            summary_excerpt=updated_resume.get("summary_excerpt"),
            industry=updated_resume["industry"],
            template_id=updated_resume["template_id"],
            export_status=updated_resume.get("export_status", ExportStatus.FREE.value),
            version=updated_resume.get("version", 1),
            sections_count=updated_resume.get("sections_count"),
            word_count=updated_resume.get("word_count")
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating resume: {str(e)}")


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, user: Dict = Depends(get_current_user)):
    try:
        user_id = user["uid"]
        resume_ref = db.collection("resumes").document(resume_id)
        resume = resume_ref.get()

        if not resume.exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume_data = resume.to_dict()

        if resume_data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        resume_ref.update({
            "deleted_at": datetime.now(),
            "updated_at": datetime.now()
        })

        return {"message": "Resume deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resume: {str(e)}")


@router.post("/{resume_id}/restore")
async def restore_resume(resume_id: str, user: Dict = Depends(get_current_user)):
    try:
        user_id = user["uid"]
        resume_ref = db.collection("resumes").document(resume_id)
        resume = resume_ref.get()

        if not resume.exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume_data = resume.to_dict()

        if resume_data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        if "deleted_at" not in resume_data:
            raise HTTPException(status_code=400, detail="Resume is not deleted")

        resume_ref.update({
            "deleted_at": None,
            "updated_at": datetime.now()
        })

        return {"message": "Resume restored successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restoring resume: {str(e)}")
