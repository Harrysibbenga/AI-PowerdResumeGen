import httpx
import json
from typing import Dict, Any, Optional, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def generate_resume_with_deepseek(
    profile_data: Dict[str, Any], 
    tone: str = "professional",
    target_job_title: Optional[str] = None,
    target_job_role: Optional[str] = None,
    focus_keywords: Optional[str] = None,
    template_id: str = "modern"
) -> Dict[str, Any]:
    """
    Generate resume content using DeepSeek AI optimized for modern job market
    
    Args:
        profile_data: User profile data including experience, education, skills
        tone: Desired tone for the resume
        target_job_title: Specific job title being targeted
        target_job_role: Role level (Junior, Senior, etc.)
        focus_keywords: Keywords to emphasize
        template_id: Template style for content structure
        
    Returns:
        Dict containing structured resume sections optimized for ATS and modern hiring
    """
    try:
        # Enhanced system prompt with modern CV standards
        system_prompt = _create_enhanced_system_prompt(
            industry=profile_data.get("industry", "general"),
            tone=tone,
            target_job_title=target_job_title,
            target_job_role=target_job_role,
            focus_keywords=focus_keywords,
            template_id=template_id
        )
        
        # Prepare enhanced user content
        user_content = _prepare_user_content(profile_data, target_job_title)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.DEEPSEEK_MODEL or "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.7,
                    "max_tokens": 4000
                },
                timeout=120.0
            )
            
            if response.status_code != 200:
                logger.warning(f"DeepSeek API returned {response.status_code}, falling back to GPT")
                from app.services.gpt_service import generate_resume_with_gpt
                return await generate_resume_with_gpt(
                    profile_data, tone, target_job_title, target_job_role, focus_keywords, template_id
                )
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            try:
                resume_content = json.loads(content)
                # Post-process and validate the content
                return _post_process_resume_content(resume_content, profile_data)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing DeepSeek response as JSON: {e}")
                raise Exception("Error parsing AI response as JSON")
    
    except httpx.TimeoutException:
        logger.error("DeepSeek API request timed out")
        # Fallback to GPT service
        try:
            from app.services.gpt_service import generate_resume_with_gpt
            return await generate_resume_with_gpt(
                profile_data, tone, target_job_title, target_job_role, focus_keywords, template_id
            )
        except Exception as fallback_error:
            logger.error(f"Fallback to GPT also failed: {fallback_error}")
            raise Exception("Both DeepSeek and GPT services failed")
    
    except Exception as e:
        logger.error(f"Error in DeepSeek service: {e}")
        # Fallback to GPT service
        try:
            from app.services.gpt_service import generate_resume_with_gpt
            return await generate_resume_with_gpt(
                profile_data, tone, target_job_title, target_job_role, focus_keywords, template_id
            )
        except Exception as fallback_error:
            logger.error(f"Fallback to GPT also failed: {fallback_error}")
            raise Exception(f"Error generating resume: {str(e)}")

def _prepare_user_content(profile_data: Dict[str, Any], target_job_title: Optional[str] = None) -> str:
    """Prepare user content with context for better AI generation"""
    
    context = {
        "profile": profile_data,
        "target_position": target_job_title,
        "generation_context": {
            "current_market_trends": "Focus on remote work capabilities, digital transformation, AI/automation skills",
            "ats_optimization": "Ensure keywords match job descriptions, use standard section headers",
            "modern_expectations": "Quantified achievements, specific technologies, collaborative skills"
        }
    }
    
    return json.dumps(context, indent=2)

def _create_enhanced_system_prompt(
    industry: str, 
    tone: str, 
    target_job_title: Optional[str] = None,
    target_job_role: Optional[str] = None,
    focus_keywords: Optional[str] = None,
    template_id: str = "modern"
) -> str:
    """Create an enhanced system prompt optimized for modern job market success"""
    
    base_prompt = f"""
You are an expert resume strategist and career consultant with deep knowledge of current hiring trends, ATS systems, and industry-specific requirements. Your goal is to create a resume that maximizes the candidate's chances of getting interviews and job offers in today's competitive market.

## CORE OBJECTIVES:
1. **ATS Optimization**: Ensure 95%+ ATS compatibility with proper formatting and keyword optimization
2. **Modern Standards**: Follow 2024-2025 resume best practices and employer expectations
3. **Industry Relevance**: Tailor content to specific industry demands and current market trends
4. **Achievement Focus**: Quantify impact wherever possible using metrics, percentages, and specific outcomes
5. **Skills Alignment**: Match in-demand skills for the target role and industry

## OUTPUT FORMAT:
Generate a JSON response with these sections:
{{
    "professional_summary": "Compelling 3-4 line summary optimized for the target role",
    "core_competencies": ["List of 8-12 key skills/technologies relevant to target role"],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "duration": "Start - End Date",
            "location": "City, State/Country",
            "achievements": [
                "Quantified achievement with specific metrics and business impact",
                "Technical accomplishment highlighting relevant skills",
                "Leadership or collaboration example with measurable results"
            ]
        }}
    ],
    "education": [
        {{
            "degree": "Degree Type",
            "institution": "School Name",
            "graduation_date": "Year",
            "relevant_coursework": ["Course 1", "Course 2"] (if recent graduate),
            "honors": "Academic honors if applicable"
        }}
    ],
    "technical_skills": {{
        "programming_languages": ["If applicable"],
        "frameworks_tools": ["Relevant to industry"],
        "platforms_systems": ["Industry-specific platforms"],
        "methodologies": ["Agile, Six Sigma, etc."]
    }},
    "certifications": ["Relevant professional certifications"],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description with impact and technologies used",
            "technologies": ["Tech stack used"],
            "outcomes": "Quantified results or business impact"
        }}
    ] (if applicable),
    "additional_sections": {{
        "languages": ["Language: Proficiency level"] (if relevant),
        "volunteer_experience": ["If adds value to application"],
        "publications": ["If applicable to role"],
        "awards": ["Professional recognition"]
    }}
}}

## CURRENT MARKET INSIGHTS (2024-2025):
"""

    # Add target-specific optimization
    if target_job_title:
        base_prompt += f"""
**TARGET ROLE OPTIMIZATION for {target_job_title}:**
- Research current job market demands for {target_job_title} positions
- Include skills and keywords commonly found in {target_job_title} job postings
- Emphasize achievements relevant to {target_job_title} responsibilities
"""

    if target_job_role:
        level_guidance = {
            "Entry Level": "Focus on education, internships, projects, and transferable skills. Emphasize learning agility and foundational knowledge.",
            "Junior": "Highlight 1-3 years of experience, growing responsibilities, and skill development. Show progression and learning.",
            "Mid-Level": "Emphasize 3-7 years of experience, project leadership, and specialized expertise. Show measurable impact.",
            "Senior": "Focus on 7+ years of experience, team leadership, strategic contributions, and mentoring. Quantify business impact.",
            "Lead": "Highlight leadership experience, cross-functional collaboration, and strategic decision-making. Show team and project outcomes.",
            "Principal": "Emphasize thought leadership, technical expertise, and organizational impact. Show innovation and industry influence.",
            "Manager": "Focus on people management, team performance, budget responsibility, and organizational goals achievement.",
            "Director": "Highlight strategic leadership, department management, and business-level impact. Show P&L responsibility if applicable.",
            "VP": "Emphasize executive leadership, organizational transformation, and enterprise-level achievements.",
            "C-Level": "Focus on visionary leadership, company-wide impact, and industry leadership."
        }
        
        if target_job_role in level_guidance:
            base_prompt += f"""
**{target_job_role.upper()} LEVEL OPTIMIZATION:**
{level_guidance[target_job_role]}
"""

    # Enhanced industry-specific guidance
    industry_guidance = {
        "technology": """
**TECHNOLOGY INDUSTRY FOCUS:**
- **In-Demand Skills 2024-2025**: AI/ML, Cloud (AWS/Azure/GCP), DevOps, Cybersecurity, Data Engineering, React/Node.js, Python, Go, Rust
- **Key Metrics**: Code quality improvements, system performance gains, user adoption rates, deployment frequency
- **Modern Practices**: Emphasize agile methodologies, CI/CD, microservices, containerization, API development
- **Collaboration**: Highlight cross-functional teamwork, code reviews, technical mentoring
- **Business Impact**: Focus on user experience improvements, scalability achievements, cost optimizations
""",
        
        "cybersecurity": """
**CYBERSECURITY INDUSTRY FOCUS:**
- **Critical Skills**: Zero Trust Architecture, SIEM/SOAR, Cloud Security, AI-driven threat detection, DevSecOps
- **Compliance**: Emphasize SOC 2, ISO 27001, NIST Framework, GDPR, CCPA experience
- **Certifications**: Prioritize CISSP, CISM, CEH, GSEC, Cloud security certs (AWS Security, Azure Security)
- **Metrics**: Incident response times, vulnerability reduction percentages, security audit scores
- **Current Threats**: Show experience with ransomware, supply chain attacks, cloud misconfigurations
""",
        
        "data_science": """
**DATA SCIENCE/ANALYTICS FOCUS:**
- **Hot Skills**: Generative AI, MLOps, Real-time analytics, Edge computing, Ethical AI
- **Tools**: Python/R, TensorFlow/PyTorch, Databricks, Snowflake, dbt, Apache Spark
- **Business Value**: Revenue impact from models, efficiency gains, customer insights, prediction accuracy
- **Modern Workflow**: Emphasize MLOps, model monitoring, A/B testing, data governance
- **Communication**: Highlight stakeholder presentations, data storytelling, cross-functional collaboration
""",
        
        "finance": """
**FINANCE INDUSTRY FOCUS:**
- **Digital Transformation**: FinTech integration, automation, digital payments, blockchain/crypto understanding
- **Risk Management**: ESG reporting, stress testing, regulatory compliance (Basel III, Dodd-Frank)
- **Analytics**: Advanced Excel, SQL, Python/R, Tableau/Power BI, financial modeling
- **Metrics**: Cost savings, revenue growth, risk reduction percentages, process improvements
- **Regulations**: Stay current with SEC, FINRA, CFTC requirements and reporting
""",
        
        "healthcare": """
**HEALTHCARE INDUSTRY FOCUS:**
- **Digital Health**: Telemedicine, EHR optimization, AI in diagnostics, patient portal management
- **Compliance**: HIPAA, FDA regulations, clinical trial protocols, quality assurance
- **Technology**: Epic, Cerner, FHIR standards, healthcare APIs, medical device integration
- **Outcomes**: Patient satisfaction scores, readmission rates, cost per patient, efficiency metrics
- **Innovation**: Emphasize evidence-based practices, quality improvement initiatives
""",
        
        "marketing": """
**MARKETING/DIGITAL MARKETING FOCUS:**
- **Digital Channels**: SEO/SEM, social media marketing, content marketing, email automation, influencer partnerships
- **Analytics**: Google Analytics 4, Adobe Analytics, customer journey mapping, attribution modeling
- **Modern Tools**: HubSpot, Salesforce Marketing Cloud, Marketo, programmatic advertising
- **AI Integration**: Marketing automation, personalization engines, predictive analytics
- **Metrics**: CAC, LTV, ROAS, conversion rates, engagement metrics, pipeline contribution
""",
        
        "sales": """
**SALES INDUSTRY FOCUS:**
- **Modern Sales**: Social selling, consultative selling, account-based sales, inside sales
- **Technology**: CRM mastery (Salesforce, HubSpot), sales enablement tools, video prospecting
- **Metrics**: Quota attainment, pipeline generation, deal size growth, sales cycle reduction
- **Methodologies**: Challenger Sale, SPIN Selling, MEDDIC, consultative approaches
- **Relationship Building**: Emphasize long-term client relationships, upselling, cross-selling success
""",
        
        "product_management": """
**PRODUCT MANAGEMENT FOCUS:**
- **Modern Practices**: Agile/Scrum, Design Thinking, Lean Startup, OKRs, customer-centric development
- **Analytics**: Product analytics, A/B testing, user research, cohort analysis, feature adoption
- **Collaboration**: Cross-functional leadership, stakeholder management, engineering partnership
- **Tools**: Jira, Confluence, Figma, Mixpanel, Amplitude, roadmapping tools
- **Outcomes**: User engagement, retention rates, revenue impact, feature adoption, market share growth
""",
        
        "human_resources": """
**HUMAN RESOURCES FOCUS:**
- **Modern HR**: People analytics, DEI initiatives, remote work strategies, employee experience
- **Technology**: HRIS systems, ATS platforms, employee engagement tools, performance management systems
- **Compliance**: Employment law, workplace safety, data privacy, global HR regulations
- **Metrics**: Employee retention, engagement scores, hiring metrics, training effectiveness
- **Trends**: Emphasize mental health support, flexible work arrangements, talent development
"""
    }
    
    # Add industry-specific guidance
    industry_key = industry.lower().replace(" ", "_")
    if industry_key in industry_guidance:
        base_prompt += industry_guidance[industry_key]
    
    # Add tone-specific modifications
    tone_modifications = {
        "professional": """
**PROFESSIONAL TONE GUIDELINES:**
- Use formal, industry-standard language
- Focus on concrete achievements and responsibilities
- Maintain consistent, polished presentation
- Emphasize reliability and competence
""",
        
        "confident": """
**CONFIDENT TONE GUIDELINES:**
- Use strong action verbs (Led, Transformed, Achieved, Delivered)
- Lead with major accomplishments
- Emphasize leadership and initiative
- Show decisiveness and impact
""",
        
        "creative": """
**CREATIVE TONE GUIDELINES:**
- Highlight innovation and creative problem-solving
- Emphasize unique approaches and original thinking
- Show adaptability and experimentation
- Include creative projects and unconventional achievements
""",
        
        "achievement": """
**ACHIEVEMENT-FOCUSED GUIDELINES:**
- Every bullet point should include quantifiable results
- Lead with the outcome, then explain the action
- Use specific numbers, percentages, and metrics
- Focus on business impact over responsibilities
"""
    }
    
    if tone.lower() in tone_modifications:
        base_prompt += tone_modifications[tone.lower()]
    
    # Add focus keywords integration
    if focus_keywords:
        base_prompt += f"""
**KEYWORD OPTIMIZATION:**
Naturally integrate these focus keywords throughout the resume: {focus_keywords}
Ensure keywords appear in relevant context within achievements and skills sections.
"""
    
    # Add current market trends
    base_prompt += """
## 2024-2025 HIRING TRENDS TO CONSIDER:
- **Remote/Hybrid Work**: Emphasize virtual collaboration, self-management, digital communication
- **AI Integration**: Show adaptability to AI tools and automation in relevant roles
- **Sustainability**: Highlight ESG initiatives, sustainable practices, green technology experience
- **Diversity & Inclusion**: Emphasize inclusive leadership, diverse team management, cultural competency
- **Continuous Learning**: Show upskilling, certification pursuit, staying current with industry trends
- **Soft Skills**: Communication, emotional intelligence, adaptability, critical thinking
- **Data-Driven Decision Making**: Emphasize analytics, metrics-based approaches, evidence-based recommendations

## ATS OPTIMIZATION REQUIREMENTS:
- Use standard section headers (Professional Summary, Experience, Education, Skills)
- Include relevant keywords naturally throughout content
- Use simple formatting with clear hierarchy
- Avoid headers, footers, tables, graphics, or unusual fonts
- Use standard date formats (MM/YYYY or Month YYYY)
- Spell out acronyms at first use, then use abbreviation
- Include both technical and soft skills relevant to the role

Generate a resume that positions the candidate as the ideal fit for their target role while ensuring maximum ATS compatibility and modern hiring manager appeal.
"""

    return base_prompt

def _post_process_resume_content(resume_content: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Post-process and validate the generated resume content"""
    
    # Ensure all required sections are present
    required_sections = ["professional_summary", "experience", "education", "core_competencies"]
    for section in required_sections:
        if section not in resume_content:
            resume_content[section] = []
    
    # Validate and enhance professional summary
    if isinstance(resume_content.get("professional_summary"), str):
        summary = resume_content["professional_summary"]
        # Ensure summary is appropriately sized (100-150 words)
        words = summary.split()
        if len(words) > 150:
            resume_content["professional_summary"] = " ".join(words[:150]) + "..."
    
    # Ensure core competencies are relevant and properly formatted
    if "core_competencies" in resume_content:
        competencies = resume_content["core_competencies"]
        if isinstance(competencies, list):
            # Limit to 12 competencies max
            resume_content["core_competencies"] = competencies[:12]
    
    # Validate experience section structure
    if "experience" in resume_content and isinstance(resume_content["experience"], list):
        for exp in resume_content["experience"]:
            if "achievements" not in exp:
                exp["achievements"] = []
            # Ensure 3-5 achievements per role
            if len(exp["achievements"]) > 5:
                exp["achievements"] = exp["achievements"][:5]
    
    # Add metadata for tracking
    resume_content["_metadata"] = {
        "generated_by": "deepseek",
        "generation_timestamp": "2024",
        "ats_optimized": True,
        "industry_tailored": True
    }
    
    return resume_content

# Industry-specific skill recommendations
def get_industry_skills(industry: str) -> List[str]:
    """Get recommended skills for specific industries"""
    
    skills_map = {
        "technology": [
            "Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes",
            "Git", "Agile/Scrum", "RESTful APIs", "Microservices", "CI/CD", "DevOps"
        ],
        "cybersecurity": [
            "SIEM", "Vulnerability Assessment", "Penetration Testing", "Incident Response",
            "Risk Management", "Compliance", "Network Security", "Cloud Security", "CISSP", "CEH"
        ],
        "data_science": [
            "Python", "R", "SQL", "Machine Learning", "TensorFlow", "PyTorch", "Pandas",
            "Scikit-learn", "Tableau", "Power BI", "Apache Spark", "MLOps", "Statistics"
        ],
        "finance": [
            "Financial Modeling", "Excel", "SQL", "Python", "R", "Bloomberg Terminal",
            "Risk Management", "Financial Analysis", "Accounting", "GAAP", "CFA", "CPA"
        ],
        "marketing": [
            "Google Analytics", "SEO/SEM", "Social Media Marketing", "Content Marketing",
            "Marketing Automation", "A/B Testing", "CRM", "Email Marketing", "PPC", "Adobe Creative Suite"
        ]
    }
    
    return skills_map.get(industry.lower(), [])