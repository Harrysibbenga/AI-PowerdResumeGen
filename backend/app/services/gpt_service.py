import httpx
import json
from typing import Dict, Any
from app.core.config import settings

async def generate_resume_with_gpt(profile_data: Dict[str, Any], tone: str = "professional") -> Dict[str, Any]:
    """
    Generate resume content using OpenAI's GPT model
    
    Args:
        profile_data: User profile data including experience, education, skills
        tone: Desired tone for the resume (professional, confident, etc.)
        
    Returns:
        Dict containing structured resume sections
    """
    # Create system prompt based on industry and tone
    system_prompt = _create_system_prompt(profile_data.get("industry", "general"), tone)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.GPT_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(profile_data)}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.7
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("error", {}).get("message", "Unknown error")
                raise Exception(f"OpenAI API error: {error_detail}")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON from response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                raise Exception("Error parsing AI response as JSON")
    
    except httpx.TimeoutException:
        raise Exception("Request to OpenAI API timed out")
    except Exception as e:
        raise Exception(f"Error generating resume with GPT: {str(e)}")


def _create_system_prompt(industry: str, tone: str) -> str:
    """
    Create a tailored system prompt based on industry and tone
    
    Args:
        industry: The industry for the resume
        tone: The desired tone
        
    Returns:
        Formatted system prompt
    """
    # Start with the base prompt
    prompt = base_prompt
    
    # Add industry-specific instructions if available
    if industry.lower() in industry_prompts:
        prompt += industry_prompts[industry.lower()]
    
    # Add tone-specific instructions if available
    if tone.lower() in tone_additions:
        prompt += tone_additions[tone.lower()]
    
    return prompt
    base_prompt = """
    You are a professional resume writer with expertise in crafting compelling resumes for specialized industries.
    Create a professional resume based on the provided information. Format your response as JSON with these sections:
    1. summary - A compelling professional summary (100-150 words)
    2. experience - Enhanced bullet points for each role (3-5 bullet points per role)
    3. skills - Organized skills relevant to the industry (categorized if appropriate)
    4. education - Formatted education entries with relevant details
    
    Make the content ATS-friendly while being impactful and achievement-focused.
    Highlight quantifiable achievements and use strong action verbs.
    """
    
    # Industry-specific prompts
    industry_prompts = {
        "cybersecurity": """
            Focus on technical security skills, certifications, and experience with security tools and frameworks.
            Highlight incident response, threat detection, and security assessment experience.
            Emphasize compliance knowledge (GDPR, HIPAA, etc.) and security certifications (CISSP, CEH, etc.).
            Use specific security terminology relevant to the field.
        """,
        
        "legal": """
            Emphasize case management experience, research abilities, and specific legal domain expertise.
            Highlight client relationship management and negotiation skills.
            Focus on legal writing abilities, knowledge of specific laws/regulations, and courtroom experience if applicable.
            Mention legal technology proficiency and document management skills.
        """,
        
        "healthcare": """
            Highlight patient care experience, medical systems knowledge, and relevant certifications.
            Focus on compliance with healthcare regulations (HIPAA, etc.) and medical terminology.
            Emphasize interdisciplinary team collaboration and emergency response capabilities if applicable.
            Mention experience with electronic health records (EHR) systems.
        """,
        
        "finance": """
            Emphasize analytical skills, financial modeling expertise, and compliance knowledge.
            Highlight experience with financial systems, regulatory frameworks, and risk management.
            Focus on quantifiable achievements like cost savings, portfolio growth, or efficiency improvements.
            Mention relevant financial certifications (CFA, CPA, etc.) prominently.
        """,
        
        "tech": """
            Focus on technical skills, programming languages, and specific technologies/frameworks.
            Highlight project delivery, technical problem-solving, and system architecture experience.
            Emphasize agile methodology knowledge and collaborative development practices.
            Mention contributions to open source, patents, or technical innovations if applicable.
        """
    }
    
    # Tone-specific additions
    tone_additions = {
        "professional": """
            Maintain a balanced, formal tone throughout the resume.
            Use industry-standard terminology and clear, straightforward language.
            Focus on relevant achievements while avoiding excessive personal style.
        """,
        
        "confident": """
            Use strong, assertive language that positions the candidate as an authority.
            Lead with major achievements and career highlights.
            Emphasize leadership qualities and decisive action through word choice.
            Use powerful action verbs and definitive statements about expertise.
        """,
        
        "achievement": """
            Prioritize quantifiable results and metrics in every bullet point possible.
            Begin each experience bullet with the achievement/result rather than the action.
            Incorporate specific numbers, percentages, and measurable outcomes.
            Focus on business impact rather than just responsibilities.
        """
    }