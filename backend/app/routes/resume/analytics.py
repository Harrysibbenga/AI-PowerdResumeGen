from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Optional, List
from app.dependencies.auth_dependencies import get_current_user
from app.core.firebase import db
from app.models.resume import ResumeStats
from datetime import datetime, timedelta
from collections import defaultdict

router = APIRouter()

@router.get("/stats/overview", response_model=ResumeStats)
async def get_resume_stats(user: Dict = Depends(get_current_user)):
    """Get user's resume statistics and analytics"""
    try:
        user_id = user["uid"]
        
        # Get user's resumes (excluding soft-deleted ones)
        resumes_ref = db.collection("resumes").where("user_id", "==", user_id)
        resumes = [doc for doc in resumes_ref.stream() if "deleted_at" not in doc.to_dict()]
        
        # Get user's exports
        exports_ref = db.collection("exports").where("user_id", "==", user_id)
        exports = list(exports_ref.stream())
        
        # Calculate basic statistics
        total_resumes = len(resumes)
        total_exports = len(exports)
        
        # Group by industry and template
        industries = defaultdict(int)
        templates = defaultdict(int)
        monthly_activity = defaultdict(int)
        
        # Recent activity (last 10 activities)
        recent_activity = []
        
        for resume in resumes:
            data = resume.to_dict()
            
            # Count industries
            industry = data.get("industry", "Unknown")
            industries[industry] += 1
            
            # Count templates
            template = data.get("template_id", "Unknown")
            templates[template] += 1
            
            # Monthly activity
            created_at = data.get("created_at")
            if created_at:
                month_key = created_at.strftime("%Y-%m")
                monthly_activity[month_key] += 1
            
            # Recent activity
            recent_activity.append({
                "id": data["id"],
                "title": data["title"],
                "action": "created",
                "timestamp": data["created_at"],
                "type": "resume"
            })
        
        # Add export activities
        for export in exports:
            data = export.to_dict()
            recent_activity.append({
                "id": data["id"],
                "title": f"Exported {data.get('filename', 'resume')}",
                "action": "exported",
                "timestamp": data["created_at"],
                "type": "export"
            })
        
        # Sort recent activity by timestamp and limit to 10
        recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activity = recent_activity[:10]
        
        return ResumeStats(
            total_resumes=total_resumes,
            total_exports=total_exports,
            industries=dict(industries),
            templates=dict(templates),
            recent_activity=recent_activity
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting resume stats: {str(e)}")

@router.get("/stats/detailed")
async def get_detailed_stats(
    user: Dict = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """Get detailed analytics for the specified time period"""
    try:
        user_id = user["uid"]
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get resumes created in the period
        resumes_ref = db.collection("resumes").where("user_id", "==", user_id).where(
            "created_at", ">=", start_date
        ).where("created_at", "<=", end_date)
        
        period_resumes = [doc for doc in resumes_ref.stream() if "deleted_at" not in doc.to_dict()]
        
        # Get exports in the period
        exports_ref = db.collection("exports").where("user_id", "==", user_id).where(
            "created_at", ">=", start_date
        ).where("created_at", "<=", end_date)
        
        period_exports = list(exports_ref.stream())
        
        # Daily activity breakdown
        daily_activity = defaultdict(lambda: {"resumes": 0, "exports": 0})
        
        for resume in period_resumes:
            data = resume.to_dict()
            date_key = data["created_at"].strftime("%Y-%m-%d")
            daily_activity[date_key]["resumes"] += 1
        
        for export in period_exports:
            data = export.to_dict()
            date_key = data["created_at"].strftime("%Y-%m-%d")
            daily_activity[date_key]["exports"] += 1
        
        # Template usage trends
        template_trends = defaultdict(int)
        industry_trends = defaultdict(int)
        
        for resume in period_resumes:
            data = resume.to_dict()
            template_trends[data.get("template_id", "Unknown")] += 1
            industry_trends[data.get("industry", "Unknown")] += 1
        
        # Export format preferences
        export_formats = defaultdict(int)
        for export in period_exports:
            data = export.to_dict()
            export_formats[data.get("format", "unknown")] += 1
        
        # Average word count
        total_words = 0
        word_count_resumes = 0
        for resume in period_resumes:
            data = resume.to_dict()
            if "word_count" in data and data["word_count"]:
                total_words += data["word_count"]
                word_count_resumes += 1
        
        avg_word_count = total_words / word_count_resumes if word_count_resumes > 0 else 0
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days
            },
            "summary": {
                "resumes_created": len(period_resumes),
                "exports_completed": len(period_exports),
                "avg_word_count": round(avg_word_count, 0)
            },
            "daily_activity": dict(daily_activity),
            "template_trends": dict(template_trends),
            "industry_trends": dict(industry_trends),
            "export_formats": dict(export_formats)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting detailed stats: {str(e)}")

@router.get("/stats/performance")
async def get_performance_metrics(user: Dict = Depends(get_current_user)):
    """Get performance metrics for user's resumes"""
    try:
        user_id = user["uid"]
        
        # Get all user's resumes
        resumes_ref = db.collection("resumes").where("user_id", "==", user_id)
        resumes = [doc for doc in resumes_ref.stream() if "deleted_at" not in doc.to_dict()]
        
        if not resumes:
            return {
                "total_resumes": 0,
                "metrics": {}
            }
        
        # Calculate performance metrics
        total_word_count = 0
        total_sections = 0
        resume_count = 0
        
        template_performance = defaultdict(lambda: {
            "count": 0,
            "avg_word_count": 0,
            "avg_sections": 0,
            "total_exports": 0
        })
        
        industry_performance = defaultdict(lambda: {
            "count": 0,
            "avg_word_count": 0,
            "avg_sections": 0
        })
        
        for resume in resumes:
            data = resume.to_dict()
            resume_count += 1
            
            word_count = data.get("word_count", 0)
            sections_count = data.get("sections_count", 0)
            template_id = data.get("template_id", "Unknown")
            industry = data.get("industry", "Unknown")
            
            total_word_count += word_count
            total_sections += sections_count
            
            # Template performance
            template_performance[template_id]["count"] += 1
            template_performance[template_id]["avg_word_count"] += word_count
            template_performance[template_id]["avg_sections"] += sections_count
            
            # Count exports for this resume
            exports_for_resume = db.collection("exports").where("resume_id", "==", data["id"]).stream()
            export_count = sum(1 for _ in exports_for_resume)
            template_performance[template_id]["total_exports"] += export_count
            
            # Industry performance
            industry_performance[industry]["count"] += 1
            industry_performance[industry]["avg_word_count"] += word_count
            industry_performance[industry]["avg_sections"] += sections_count
        
        # Calculate averages
        for template in template_performance:
            count = template_performance[template]["count"]
            if count > 0:
                template_performance[template]["avg_word_count"] /= count
                template_performance[template]["avg_sections"] /= count
        
        for industry in industry_performance:
            count = industry_performance[industry]["count"]
            if count > 0:
                industry_performance[industry]["avg_word_count"] /= count
                industry_performance[industry]["avg_sections"] /= count
        
        return {
            "total_resumes": resume_count,
            "overall_metrics": {
                "avg_word_count": round(total_word_count / resume_count, 0) if resume_count > 0 else 0,
                "avg_sections": round(total_sections / resume_count, 1) if resume_count > 0 else 0
            },
            "template_performance": dict(template_performance),
            "industry_performance": dict(industry_performance)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")

@router.get("/trending")
async def get_trending_data(user: Dict = Depends(get_current_user)):
    """Get trending templates, industries, and keywords across the platform"""
    try:
        # Note: This would typically be cached and updated periodically
        # For now, we'll calculate from recent data
        
        # Get recent resumes (last 30 days) from all users for trending data
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        recent_resumes_ref = db.collection("resumes").where("created_at", ">=", thirty_days_ago)
        recent_resumes = [doc for doc in recent_resumes_ref.stream() if "deleted_at" not in doc.to_dict()]
        
        # Count trending items
        trending_templates = defaultdict(int)
        trending_industries = defaultdict(int)
        trending_keywords = defaultdict(int)
        
        for resume in recent_resumes:
            data = resume.to_dict()
            
            # Count templates
            template = data.get("template_id", "")
            if template:
                trending_templates[template] += 1
            
            # Count industries
            industry = data.get("industry", "")
            if industry:
                trending_industries[industry] += 1
            
            # Count keywords from focus_keywords
            keywords = data.get("focus_keywords", "")
            if keywords:
                # Simple keyword extraction
                for keyword in keywords.split():
                    clean_keyword = keyword.strip().lower()
                    if len(clean_keyword) > 2:  # Ignore very short words
                        trending_keywords[clean_keyword] += 1
        
        # Sort and limit results
        trending_templates = dict(sorted(trending_templates.items(), key=lambda x: x[1], reverse=True)[:10])
        trending_industries = dict(sorted(trending_industries.items(), key=lambda x: x[1], reverse=True)[:10])
        trending_keywords = dict(sorted(trending_keywords.items(), key=lambda x: x[1], reverse=True)[:20])
        
        return {
            "period": "last_30_days",
            "trending_templates": trending_templates,
            "trending_industries": trending_industries,
            "trending_keywords": trending_keywords,
            "total_resumes_analyzed": len(recent_resumes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trending data: {str(e)}")