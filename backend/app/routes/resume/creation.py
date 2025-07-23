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

router = APIRouter()

@router.post("/", response_model=ResumeResponse)
async def create_resume(
    request: ResumeRequest,
    user: Dict = Depends(get_current_user)
):
    """Create a new resume with AI generation"""
    try:
        user_id = user["uid"]

        # Validate user input
        if not request.profile.workExperience and not request.profile.education:
            raise HTTPException(
                status_code=400, 
                detail="At least one work experience or education entry is required"
            )

        # Generate resume content using AI
        if settings.USE_DEEPSEEK and settings.DEEPSEEK_API_KEY:
            resume_content = await generate_resume_with_deepseek(
                profile_data=request.profile.dict(), 
                tone=request.aiTone.value,  
                target_job_title=request.targetJobTitle,  
                target_job_role=request.targetJobRole,   
                focus_keywords=request.focusKeywords,    
                template_id=request.template_id.value
            )
        else:
            resume_content = await generate_resume_with_gpt(
                profile_data=request.profile.dict(), 
                tone=request.aiTone.value,  
                target_job_title=request.targetJobTitle,  
                target_job_role=request.targetJobRole,   
                focus_keywords=request.focusKeywords,    
                template_id=request.template_id.value
            )

        # Generate summary excerpt for card display
        summary_excerpt = generate_summary_excerpt(resume_content)

        # Create resume document
        resume_id = str(uuid.uuid4())
        resume_ref = db.collection("resumes").document(resume_id)

        resume_data = {
            "id": resume_id,
            "user_id": user_id,
            "title": request.title,
            "target_job_title": request.targetJobTitle,      
            "target_job_role": request.targetJobRole,        
            "target_company": request.targetCompany,         
            "industry": request.profile.industry,
            "template_id": request.template_id.value,
            "tone": request.aiTone.value,                    
            "length": request.aiLength.value,                
            "focus_keywords": request.focusKeywords,         
            "use_ai": request.useAI,                         
            "include_projects": request.includeProjects,     
            "include_certifications": request.includeCertifications,  
            "include_languages": request.includeLanguages,   
            "profile_data": request.profile.dict(),
            "ai_content": resume_content,
            "summary_excerpt": summary_excerpt,
            "sections_count": count_resume_sections(resume_content),
            "word_count": estimate_word_count(resume_content),
            "export_status": ExportStatus.FREE.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "version": 1
        }

        # Add custom sections if provided
        if request.custom_sections:
            resume_data["custom_sections"] = request.custom_sections

        resume_ref.set(resume_data)

        return ResumeResponse(
            id=resume_id,
            title=request.title,
            target_job_title=request.targetJobTitle, 
            target_job_role=request.targetJobRole,  
            sections=resume_content,
            message="Resume generated successfully!",
            created_at=resume_data["created_at"],
            summary_excerpt=summary_excerpt,
            industry=request.profile.industry,
            template_id=request.template_id,
            export_status=ExportStatus.FREE
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")

@router.post("/duplicate/{resume_id}", response_model=ResumeResponse)
async def duplicate_resume(
    resume_id: str,
    user: Dict = Depends(get_current_user)
):
    """Duplicate an existing resume"""
    try:
        user_id = user["uid"]
        
        # Get original resume
        original_ref = db.collection("resumes").document(resume_id)
        original = original_ref.get()

        if not original.exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        original_data = original.to_dict()

        if original_data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Create new resume with duplicated data
        new_resume_id = str(uuid.uuid4())
        new_resume_ref = db.collection("resumes").document(new_resume_id)

        # Copy data and update relevant fields
        new_resume_data = original_data.copy()
        new_resume_data.update({
            "id": new_resume_id,
            "title": f"{original_data['title']} (Copy)",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "export_status": ExportStatus.FREE.value,
            "version": 1
        })

        new_resume_ref.set(new_resume_data)

        return ResumeResponse(
            id=new_resume_id,
            title=new_resume_data["title"],
            target_job_title=new_resume_data.get("target_job_title", new_resume_data.get("targetJobTitle")),  # Handle both field names
            target_job_role=new_resume_data.get("target_job_role", new_resume_data.get("targetJobRole")),    # Handle both field names
            sections=new_resume_data["ai_content"],
            message="Resume duplicated successfully!",
            created_at=new_resume_data["created_at"],
            summary_excerpt=new_resume_data.get("summary_excerpt"),
            industry=new_resume_data["industry"],
            template_id=new_resume_data["template_id"],
            export_status=ExportStatus.FREE
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error duplicating resume: {str(e)}")

@router.post("/regenerate/{resume_id}", response_model=ResumeResponse)
async def regenerate_resume_content(
    resume_id: str,
    user: Dict = Depends(get_current_user)
):
    """Regenerate AI content for an existing resume"""
    try:
        user_id = user["uid"]
        
        # Get existing resume
        resume_ref = db.collection("resumes").document(resume_id)
        resume = resume_ref.get()

        if not resume.exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume_data = resume.to_dict()

        if resume_data["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Extract data with fallbacks for field name changes
        target_job_title = resume_data.get("target_job_title") or resume_data.get("targetJobTitle")
        target_job_role = resume_data.get("target_job_role") or resume_data.get("targetJobRole")
        tone = resume_data.get("tone") or resume_data.get("aiTone", "professional")
        focus_keywords = resume_data.get("focus_keywords") or resume_data.get("focusKeywords")

        # Regenerate AI content
        if settings.USE_DEEPSEEK and settings.DEEPSEEK_API_KEY:
            new_content = await generate_resume_with_deepseek(
                profile_data=resume_data["profile_data"], 
                tone=tone,
                target_job_title=target_job_title,
                target_job_role=target_job_role,
                focus_keywords=focus_keywords,
                template_id=resume_data["template_id"]
            )
        else:
            new_content = await generate_resume_with_gpt(
                profile_data=resume_data["profile_data"], 
                tone=tone,
                target_job_title=target_job_title,
                target_job_role=target_job_role,
                focus_keywords=focus_keywords,
                template_id=resume_data["template_id"]
            )

        # Update resume with new content
        updates = {
            "ai_content": new_content,
            "summary_excerpt": generate_summary_excerpt(new_content),
            "sections_count": count_resume_sections(new_content),
            "word_count": estimate_word_count(new_content),
            "updated_at": datetime.now(),
            "version": resume_data.get("version", 1) + 1
        }

        resume_ref.update(updates)
        
        # Return updated resume
        updated_data = {**resume_data, **updates}

        return ResumeResponse(
            id=resume_id,
            title=updated_data["title"],
            target_job_title=target_job_title,  # Use extracted value
            target_job_role=target_job_role,    # Use extracted value
            sections=updated_data["ai_content"],
            message="Resume content regenerated successfully!",
            created_at=updated_data["created_at"],
            summary_excerpt=updated_data["summary_excerpt"],
            industry=updated_data["industry"],
            template_id=updated_data["template_id"],
            export_status=updated_data["export_status"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating resume: {str(e)}")

# Optional: Helper function to normalize field names across old/new data
def normalize_resume_data(resume_data):
    """Helper to handle field name transitions in stored data"""
    normalized = resume_data.copy()
    
    # Handle field name mappings
    field_mappings = {
        "targetJobTitle": "target_job_title",
        "targetJobRole": "target_job_role", 
        "targetCompany": "target_company",
        "aiTone": "tone",
        "aiLength": "length",
        "focusKeywords": "focus_keywords",
        "includeProjects": "include_projects",
        "includeCertifications": "include_certifications",
        "includeLanguages": "include_languages",
        "useAI": "use_ai"
    }
    
    # Map new field names to old ones if they exist
    for new_field, old_field in field_mappings.items():
        if new_field in normalized and old_field not in normalized:
            normalized[old_field] = normalized[new_field]
        elif old_field in normalized and new_field not in normalized:
            normalized[new_field] = normalized[old_field]
    
    return normalized