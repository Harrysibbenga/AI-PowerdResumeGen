"""
Resume utility functions for processing and analyzing resume data
"""
from typing import Dict, Any, List
import re
from datetime import datetime

def generate_summary_excerpt(sections: Dict[str, Any], max_words: int = 50) -> str:
    """
    Generate a summary excerpt from resume sections for card display
    
    Args:
        sections: Dictionary containing resume sections
        max_words: Maximum number of words in the excerpt
        
    Returns:
        A summary excerpt string
    """
    try:
        # Priority order for extracting summary
        summary_sources = [
            'professional_summary',
            'summary',
            'objective',
            'profile'
        ]
        
        # Try to extract from professional summary first
        for source in summary_sources:
            if source in sections and sections[source]:
                summary = sections[source]
                if isinstance(summary, str) and summary.strip():
                    return _truncate_text(summary.strip(), max_words)
        
        # Fallback to experience description
        if 'experience' in sections and sections['experience']:
            experience = sections['experience']
            if isinstance(experience, list) and len(experience) > 0:
                exp = experience[0]
                if isinstance(exp, dict) and 'description' in exp:
                    description = exp['description']
                    if isinstance(description, str) and description.strip():
                        return _truncate_text(description.strip(), max_words)
            elif isinstance(experience, dict) and 'description' in experience:
                description = experience['description']
                if isinstance(description, str) and description.strip():
                    return _truncate_text(description.strip(), max_words)
        
        # Fallback to education or skills
        if 'education' in sections and sections['education']:
            education = sections['education']
            if isinstance(education, list) and len(education) > 0:
                edu = education[0]
                if isinstance(edu, dict):
                    degree = edu.get('degree', '')
                    institution = edu.get('institution', '')
                    if degree and institution:
                        return f"{degree} graduate from {institution}"
        
        # Final fallback
        return "Professional resume generated with AI assistance"
        
    except Exception:
        return "Professional resume generated with AI assistance"

def _truncate_text(text: str, max_words: int) -> str:
    """Truncate text to specified number of words"""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'

def count_resume_sections(sections: Dict[str, Any]) -> int:
    """
    Count the number of populated sections in a resume
    
    Args:
        sections: Dictionary containing resume sections
        
    Returns:
        Number of sections with content
    """
    # Define sections to count
    countable_sections = [
        'personal_info', 'contact_info',
        'professional_summary', 'summary', 'objective',
        'experience', 'work_experience',
        'education',
        'skills', 'technical_skills', 'core_competencies',
        'projects',
        'certifications', 'certificates',
        'languages',
        'achievements', 'accomplishments',
        'awards',
        'publications',
        'volunteer',
        'interests', 'hobbies'
    ]
    
    count = 0
    
    for section in countable_sections:
        if section in sections and _is_section_populated(sections[section]):
            count += 1
    
    # Count any custom sections
    for key, value in sections.items():
        if key not in countable_sections and _is_section_populated(value):
            count += 1
    
    return count

def _is_section_populated(value: Any) -> bool:
    """Check if a section has meaningful content"""
    if value is None:
        return False
    
    if isinstance(value, str):
        return bool(value.strip())
    
    if isinstance(value, list):
        return len(value) > 0 and any(_is_section_populated(item) for item in value)
    
    if isinstance(value, dict):
        return any(_is_section_populated(v) for v in value.values())
    
    return bool(value)

def estimate_word_count(sections: Dict[str, Any]) -> int:
    """
    Estimate total word count of resume content
    
    Args:
        sections: Dictionary containing resume sections
        
    Returns:
        Estimated word count
    """
    def count_words_in_value(value: Any) -> int:
        if isinstance(value, str):
            # Remove extra whitespace and count words
            clean_text = re.sub(r'\s+', ' ', value.strip())
            return len(clean_text.split()) if clean_text else 0
        
        elif isinstance(value, list):
            return sum(count_words_in_value(item) for item in value)
        
        elif isinstance(value, dict):
            return sum(count_words_in_value(v) for v in value.values())
        
        return 0
    
    return count_words_in_value(sections)

def extract_keywords(sections: Dict[str, Any], min_length: int = 3) -> List[str]:
    """
    Extract relevant keywords from resume content
    
    Args:
        sections: Dictionary containing resume sections
        min_length: Minimum length of keywords to extract
        
    Returns:
        List of extracted keywords
    """
    # Common stop words to exclude
    stop_words = {
        'and', 'or', 'but', 'the', 'a', 'an', 'is', 'was', 'are', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
        'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'without',
        'from', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'when', 'where',
        'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
        'own', 'same', 'so', 'than', 'too', 'very'
    }
    
    def extract_text(value: Any) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            return ' '.join(extract_text(item) for item in value)
        elif isinstance(value, dict):
            return ' '.join(extract_text(v) for v in value.values())
        return str(value) if value else ''
    
    # Extract all text content
    all_text = extract_text(sections)
    
    # Extract words using regex
    words = re.findall(r'\b[a-zA-Z]+\b', all_text.lower())
    
    # Filter words
    keywords = [
        word for word in words 
        if len(word) >= min_length and word not in stop_words
    ]
    
    # Count frequency and return unique keywords
    from collections import Counter
    word_counts = Counter(keywords)
    
    # Return keywords sorted by frequency
    return [word for word, count in word_counts.most_common(50)]

def calculate_resume_score(sections: Dict[str, Any], target_job_title: str = None) -> Dict[str, Any]:
    """
    Calculate a completeness score for the resume
    
    Args:
        sections: Dictionary containing resume sections
        target_job_title: Optional target job title for scoring context
        
    Returns:
        Dictionary with score and recommendations
    """
    score = 0
    max_score = 100
    recommendations = []
    
    # Essential sections (60 points total)
    essential_checks = [
        ('contact_info', 15, 'Add complete contact information'),
        ('professional_summary', 15, 'Add a professional summary'),
        ('experience', 20, 'Add work experience'),
        ('skills', 10, 'Add relevant skills')
    ]
    
    for section, points, recommendation in essential_checks:
        if section in sections and _is_section_populated(sections[section]):
            score += points
        else:
            recommendations.append(recommendation)
    
    # Important sections (30 points total)
    important_checks = [
        ('education', 15, 'Add education information'),
        ('achievements', 10, 'Highlight key achievements'),
        ('certifications', 5, 'Add relevant certifications')
    ]
    
    for section, points, recommendation in important_checks:
        if section in sections and _is_section_populated(sections[section]):
            score += points
        else:
            recommendations.append(recommendation)
    
    # Optional sections (10 points total)
    optional_checks = [
        ('projects', 5, 'Consider adding projects'),
        ('languages', 3, 'Add language skills if relevant'),
        ('volunteer', 2, 'Consider adding volunteer experience')
    ]
    
    for section, points, recommendation in optional_checks:
        if section in sections and _is_section_populated(sections[section]):
            score += points
    
    # Word count bonus/penalty
    word_count = estimate_word_count(sections)
    if word_count < 200:
        recommendations.append('Consider expanding content - resume seems too brief')
    elif word_count > 800:
        recommendations.append('Consider condensing content - resume might be too lengthy')
    
    # Determine score category
    if score >= 90:
        category = 'Excellent'
    elif score >= 75:
        category = 'Good'
    elif score >= 60:
        category = 'Fair'
    else:
        category = 'Needs Improvement'
    
    return {
        'score': score,
        'max_score': max_score,
        'percentage': round((score / max_score) * 100, 1),
        'category': category,
        'word_count': word_count,
        'sections_count': count_resume_sections(sections),
        'recommendations': recommendations[:5]  # Limit to top 5 recommendations
    }

def format_resume_metadata(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format resume metadata for consistent API responses
    
    Args:
        resume_data: Raw resume data from database
        
    Returns:
        Formatted metadata dictionary
    """
    return {
        'id': resume_data.get('id'),
        'title': resume_data.get('title'),
        'target_job_title': resume_data.get('target_job_title'),
        'target_job_role': resume_data.get('target_job_role'),
        'target_company': resume_data.get('target_company'),
        'industry': resume_data.get('industry'),
        'template_id': resume_data.get('template_id'),
        'tone': resume_data.get('tone'),
        'created_at': resume_data.get('created_at'),
        'updated_at': resume_data.get('updated_at'),
        'export_status': resume_data.get('export_status', 'free'),
        'summary_excerpt': resume_data.get('summary_excerpt'),
        'sections_count': resume_data.get('sections_count', 0),
        'word_count': resume_data.get('word_count', 0),
        'version': resume_data.get('version', 1)
    }