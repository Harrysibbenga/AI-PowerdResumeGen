from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Optional
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
from datetime import datetime

router = APIRouter()

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str, user: Dict = Depends(get_current_user)):
    """Get a specific resume by ID"""
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
            sections=resume_data["ai_content"],
            message="Resume retrieved successfully",
            created_at=resume_data["created_at"],
            summary_excerpt=resume_data.get("summary_excerpt"),
            industry=resume_data["industry"],
            template_id=resume_data["template_id"],
            export_status=resume_data.get("export_status", ExportStatus.FREE.value)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resume: {str(e)}")

@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    user: Dict = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    template: Optional[str] = Query(None, description="Filter by template"),
    search: Optional[str] = Query(None, description="Search in title, job title, or role"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
):
    """List user's resumes with pagination, filtering, and sorting"""
    try:
        user_id = user["uid"]
        
        # Build base query
        query = db.collection("resumes").where("user_id", "==", user_id)
        
        # Apply filters
        if industry:
            query = query.where("industry", "==", industry)
        if template:
            query = query.where("template_id", "==", template)
        
        # Get all documents for total count and filtering
        all_docs = list(query.stream())
        
        # Apply search filter and deleted_at filter
        filtered_docs = []
        for doc in all_docs:
            data = doc.to_dict()
            
            # Filter out resumes that have deleted_at field
            if "deleted_at" in data:
                continue
            
            if search:
                search_text = f"{data.get('title', '')} {data.get('target_job_title', '')} {data.get('target_job_role', '')}".lower()
                if search.lower() not in search_text:
                    continue
            
            filtered_docs.append(data)
        
        total = len(filtered_docs)
        
        # Apply sorting
        reverse_sort = sort_order == "desc"
        if sort_by == "created_at":
            filtered_docs.sort(key=lambda x: x.get("created_at", datetime.min), reverse=reverse_sort)
        elif sort_by == "updated_at":
            filtered_docs.sort(key=lambda x: x.get("updated_at", datetime.min), reverse=reverse_sort)
        elif sort_by == "title":
            filtered_docs.sort(key=lambda x: x.get("title", "").lower(), reverse=reverse_sort)
        elif sort_by == "industry":
            filtered_docs.sort(key=lambda x: x.get("industry", "").lower(), reverse=reverse_sort)
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_docs = filtered_docs[start_idx:end_idx]
        
        # Convert to ResumeListItem objects
        resumes = []
        for data in paginated_docs:
            resumes.append(ResumeListItem(
                id=data["id"],
                title=data["title"],
                target_job_title=data["target_job_title"],
                target_job_role=data.get("target_job_role"),
                target_company=data.get("target_company"),
                industry=data["industry"],
                template_id=data["template_id"],
                export_status=data.get("export_status", ExportStatus.FREE.value),
                created_at=data["created_at"],
                updated_at=data.get("updated_at"),
                summary_excerpt=data.get("summary_excerpt"),
                sections_count=data.get("sections_count", 0),
                word_count=data.get("word_count")
            ))
        
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
    """Update an existing resume"""
    try:
        user_id = user["uid"]
        resume_ref = db.collection("resumes").document(resume_id)
        resume = resume_ref.get()

        if not resume.exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume_data = resume.to_dict()

        if resume_data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Prepare updates
        updates = {"updated_at": datetime.now()}
        regenerate_content = False
        
        # Update basic fields
        if request.title:
            updates["title"] = request.title
        if request.target_job_title:
            updates["target_job_title"] = request.target_job_title
            regenerate_content = True
        if request.target_job_role:
            updates["target_job_role"] = request.target_job_role
            regenerate_content = True
        if request.target_company:
            updates["target_company"] = request.target_company
        if request.tone:
            updates["tone"] = request.tone.value
            regenerate_content = True
        if request.template_id:
            updates["template_id"] = request.template_id.value
            regenerate_content = True
        if request.focus_keywords:
            updates["focus_keywords"] = request.focus_keywords
            regenerate_content = True

        # If profile is updated, regenerate content
        if request.profile:
            updates["profile_data"] = request.profile.dict()
            updates["industry"] = request.profile.industry
            regenerate_content = True

        # Regenerate AI content if needed
        if regenerate_content:
            profile_data = request.profile.dict() if request.profile else resume_data["profile_data"]
            tone = request.tone.value if request.tone else resume_data["tone"]
            target_job_title = request.target_job_title or resume_data["target_job_title"]
            target_job_role = request.target_job_role or resume_data.get("target_job_role")
            focus_keywords = request.focus_keywords or resume_data.get("focus_keywords")
            template_id = request.template_id.value if request.template_id else resume_data["template_id"]
            
            if settings.USE_DEEPSEEK and settings.DEEPSEEK_API_KEY:
                new_content = await generate_resume_with_deepseek(
                    profile_data=profile_data,
                    tone=tone,
                    target_job_title=target_job_title,
                    target_job_role=target_job_role,
                    focus_keywords=focus_keywords,
                    template_id=template_id
                )
            else:
                new_content = await generate_resume_with_gpt(
                    profile_data=profile_data,
                    tone=tone,
                    target_job_title=target_job_title,
                    target_job_role=target_job_role,
                    focus_keywords=focus_keywords,
                    template_id=template_id
                )
            
            updates["ai_content"] = new_content
            updates["summary_excerpt"] = generate_summary_excerpt(new_content)
            updates["sections_count"] = count_resume_sections(new_content)
            updates["word_count"] = estimate_word_count(new_content)
            updates["version"] = resume_data.get("version", 1) + 1

        # Apply updates
        resume_ref.update(updates)
        
        # Return updated resume
        updated_resume = resume_ref.get().to_dict()
        
        return ResumeResponse(
            id=updated_resume["id"],
            title=updated_resume["title"],
            target_job_title=updated_resume["target_job_title"],
            target_job_role=updated_resume.get("target_job_role"),
            sections=updated_resume["ai_content"],
            message="Resume updated successfully!",
            created_at=updated_resume["created_at"],
            summary_excerpt=updated_resume.get("summary_excerpt"),
            industry=updated_resume["industry"],
            template_id=updated_resume["template_id"],
            export_status=updated_resume.get("export_status", ExportStatus.FREE.value)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating resume: {str(e)}")

@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, user: Dict = Depends(get_current_user)):
    """Delete a resume"""
    try:
        user_id = user["uid"]
        resume_ref = db.collection("resumes").document(resume_id)
        resume = resume_ref.get()

        if not resume.exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume_data = resume.to_dict()

        if resume_data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Soft delete by adding deleted_at timestamp
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
    """Restore a soft-deleted resume"""
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

        # Remove deleted_at field to restore
        resume_ref.update({
            "deleted_at": None,
            "updated_at": datetime.now()
        })
        
        return {"message": "Resume restored successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restoring resume: {str(e)}")