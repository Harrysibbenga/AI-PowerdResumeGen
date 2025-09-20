import httpx
import json
from typing import Dict, Any, Optional, List
from app.core.config import settings
import logging
from datetime import datetime

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
        # Enhanced system prompt with modern AI prompting techniques
        system_prompt = _create_enhanced_system_prompt(
            industry=profile_data.get("industry", "general"),
            tone=tone,
            target_job_title=target_job_title,
            target_job_role=target_job_role,
            focus_keywords=focus_keywords,
            template_id=template_id
        )
        
        # Prepare structured user content
        user_content = _prepare_user_content(profile_data, target_job_title, focus_keywords)
        
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
                    "temperature": 0.3,  # Lower temperature for more consistent output
                    "max_tokens": 4000,
                    "top_p": 0.95  # Add top_p for better quality
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
                logger.error(f"Raw response: {content}")
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

def _prepare_user_content(
    profile_data: Dict[str, Any], 
    target_job_title: Optional[str] = None,
    focus_keywords: Optional[str] = None
) -> str:
    """Prepare structured user content for better AI understanding"""
    
    # Extract and structure the key information
    user_context = {
        "candidate_profile": {
            "personal_info": {
                "name": profile_data.get("fullName", ""),
                "email": profile_data.get("email", ""),
                "location": profile_data.get("location", ""),
                "industry": profile_data.get("industry", "")
            },
            "work_experience": profile_data.get("workExperience", []),
            "education": profile_data.get("education", []),
            "skills": profile_data.get("skills", []),
            "projects": profile_data.get("projects", []),
            "certifications": profile_data.get("certifications", []),
            "languages": profile_data.get("languages", []),
            "current_summary": profile_data.get("summary", "")
        },
        "target_position": {
            "job_title": target_job_title or "Not specified",
            "focus_keywords": focus_keywords.split(", ") if focus_keywords else [],
        },
        "instructions": {
            "optimize_for": "ATS systems and human recruiters",
            "emphasize": "quantified achievements and relevant skills",
            "format": "professional and modern",
            "length": "1-2 pages equivalent"
        }
    }
    
    return json.dumps(user_context, indent=2, default=str)

def _create_enhanced_system_prompt(
    industry: str, 
    tone: str, 
    target_job_title: Optional[str] = None,
    target_job_role: Optional[str] = None,
    focus_keywords: Optional[str] = None,
    template_id: str = "modern"
) -> str:
    """Create an enhanced system prompt using modern AI prompting techniques"""
    
    # Get current year for relevance
    current_year = datetime.now().year
    
    base_prompt = f"""You are a world-class resume strategist and career consultant specializing in creating high-impact resumes that secure interviews and job offers. You have deep expertise in ATS optimization, modern hiring practices, and industry-specific requirements for {current_year}.

# CORE MISSION
Transform the provided candidate information into a compelling, ATS-optimized resume that positions them as the ideal candidate for their target role.

# CRITICAL SUCCESS FACTORS
1. **ATS Compatibility**: 95%+ pass rate through Applicant Tracking Systems
2. **Quantified Impact**: Every achievement includes specific metrics and outcomes
3. **Keyword Optimization**: Strategic placement of industry-relevant terms
4. **Modern Standards**: Follows {current_year} best practices and employer expectations
5. **Compelling Narrative**: Creates a cohesive story of professional growth and value

# OUTPUT STRUCTURE
Generate a JSON response with the following exact structure:

```json
{{
    "professional_summary": "Compelling 2-3 sentence summary that immediately communicates value proposition",
    "core_competencies": ["8-12 relevant skills/technologies ranked by importance"],
    "professional_experience": [
        {{
            "job_title": "Exact title from input",
            "company_name": "Company name",
            "employment_period": "MM/YYYY - MM/YYYY or Present",
            "location": "City, State/Country",
            "key_achievements": [
                "Achievement with specific metrics (increased X by Y%, reduced Z by N hours)",
                "Technical accomplishment highlighting relevant skills and impact",
                "Leadership/collaboration example with quantified results"
            ]
        }}
    ],
    "education": [
        {{
            "degree": "Degree type and field",
            "institution": "University/School name",
            "graduation_date": "MM/YYYY",
            "relevant_details": "GPA (if 3.5+), honors, relevant coursework for recent grads"
        }}
    ],
    "technical_skills": {{
        "primary_technologies": ["Most important tools/languages for target role"],
        "secondary_skills": ["Supporting technologies and methodologies"],
        "certifications": ["Professional certifications and their status"]
    }},
    "notable_projects": [
        {{
            "project_name": "Clear, descriptive name",
            "description": "Brief description emphasizing impact and technologies",
            "key_technologies": ["Relevant tech stack"],
            "measurable_outcome": "Specific results or business impact"
        }}
    ]
}}
```

# OPTIMIZATION GUIDELINES"""

    # Add role-specific optimization
    if target_job_title:
        base_prompt += f"""

## TARGET ROLE OPTIMIZATION: {target_job_title}
- Research and incorporate keywords commonly found in {target_job_title} job descriptions
- Emphasize experiences and skills most relevant to {target_job_title} responsibilities
- Structure achievements to highlight progression toward {target_job_title} competencies
- Use industry-standard terminology for {target_job_title} positions"""

    # Add seniority level guidance
    if target_job_role:
        seniority_guidance = {
            "Entry Level": {
                "focus": "Education, internships, projects, and transferable skills",
                "achievements": "Learning agility, academic projects, internship contributions",
                "structure": "Education section prominent, project section detailed"
            },
            "Junior": {
                "focus": "1-3 years experience, skill development, growing responsibilities",
                "achievements": "Individual contributions, skill acquisition, process improvements",
                "structure": "Balanced experience and education, highlight growth trajectory"
            },
            "Mid-Level": {
                "focus": "3-7 years experience, project ownership, specialized expertise",
                "achievements": "Project leadership, technical expertise, cross-functional collaboration",
                "structure": "Experience-heavy, quantified individual impact"
            },
            "Senior": {
                "focus": "7+ years experience, strategic thinking, mentoring others",
                "achievements": "Team leadership, strategic initiatives, measurable business impact",
                "structure": "Leadership examples, business-level metrics, industry recognition"
            },
            "Lead/Principal": {
                "focus": "Technical leadership, architecture decisions, industry influence",
                "achievements": "System design, technical strategy, team development, innovation",
                "structure": "Technical depth, thought leadership, organizational impact"
            },
            "Manager/Director": {
                "focus": "People management, strategic planning, P&L responsibility",
                "achievements": "Team performance, budget management, strategic execution",
                "structure": "Leadership metrics, organizational transformation, business results"
            }
        }
        
        if target_job_role in seniority_guidance:
            guidance = seniority_guidance[target_job_role]
            base_prompt += f"""

## {target_job_role.upper()} LEVEL STRATEGY
- **Primary Focus**: {guidance['focus']}
- **Achievement Types**: {guidance['achievements']}
- **Content Structure**: {guidance['structure']}"""

    # Add industry-specific optimization
    industry_prompts = {
        "technology": f"""

## TECHNOLOGY INDUSTRY OPTIMIZATION ({current_year})
**High-Demand Skills**: AI/ML, Cloud Architecture (AWS/Azure/GCP), DevSecOps, Kubernetes, Microservices, React/Vue, Python/Go, Data Engineering
**Key Metrics**: System performance improvements, deployment frequency, code quality scores, user adoption rates, infrastructure cost savings
**Modern Practices**: Agile/DevOps, CI/CD pipelines, test-driven development, API-first design, observability
**Business Impact**: User experience enhancements, scalability achievements, security improvements, automation gains""",

        "cybersecurity": f"""

## CYBERSECURITY INDUSTRY OPTIMIZATION ({current_year})
**Critical Skills**: Zero Trust Architecture, AI-powered threat detection, Cloud Security Posture Management, DevSecOps, Identity Management
**Compliance Focus**: SOC 2 Type II, ISO 27001, NIST Cybersecurity Framework, GDPR/CCPA, PCI DSS
**Key Metrics**: Incident response time reduction, vulnerability remediation rates, security awareness training effectiveness, risk score improvements
**Modern Threats**: Ransomware defense, supply chain security, cloud misconfigurations, AI/ML security""",

        "data_science": f"""

## DATA SCIENCE OPTIMIZATION ({current_year})
**Cutting-Edge Skills**: Generative AI, MLOps, Real-time ML, Federated Learning, Responsible AI, AutoML
**Technical Stack**: Python/R, TensorFlow/PyTorch, Kubernetes, MLflow, Databricks, Snowflake, dbt, Apache Airflow
**Business Metrics**: Model performance improvements, prediction accuracy, revenue impact, cost savings, operational efficiency
**Modern Workflow**: MLOps pipelines, A/B testing, model monitoring, feature stores, data governance""",

        "finance": f"""

## FINANCE INDUSTRY OPTIMIZATION ({current_year})
**Digital Skills**: FinTech integration, blockchain/DeFi understanding, automated reporting, ESG analytics, regulatory technology
**Technical Proficiency**: Advanced Excel, SQL, Python/R, Tableau/Power BI, financial modeling, risk management systems
**Regulatory Knowledge**: Basel III/IV, IFRS, SOX compliance, stress testing, climate risk reporting
**Key Metrics**: Cost reduction percentages, revenue growth, risk-adjusted returns, process automation savings""",

        "marketing": f"""

## MARKETING OPTIMIZATION ({current_year})
**Digital Expertise**: Performance marketing, marketing automation, customer data platforms, AI-powered personalization, voice/visual search optimization
**Analytics Mastery**: Customer journey mapping, attribution modeling, predictive analytics, cohort analysis, lifetime value optimization
**Technology Stack**: HubSpot/Marketo, Salesforce Marketing Cloud, Google Analytics 4, Adobe Experience Platform, programmatic advertising
**Performance Metrics**: Customer acquisition cost, lifetime value, marketing qualified leads, attribution accuracy, campaign ROI""",

        "customer_service": f"""

## CUSTOMER SERVICE INDUSTRY OPTIMIZATION ({current_year})
**Modern Skills**: Omnichannel support, CRM mastery, AI chatbot management, social media customer care, video support, self-service optimization
**Technology Proficiency**: Zendesk, Salesforce Service Cloud, Intercom, LiveChat, knowledge base management, ticketing systems
**Communication Excellence**: Active listening, empathy, de-escalation, multilingual support, written communication, phone etiquette
**Key Metrics**: Customer satisfaction (CSAT), Net Promoter Score (NPS), first-call resolution, average handle time, customer retention rates
**Modern Trends**: Proactive support, customer success focus, emotional intelligence, remote support capabilities""",

        "healthcare": f"""

## HEALTHCARE INDUSTRY OPTIMIZATION ({current_year})
**Digital Health**: Telemedicine, EHR optimization (Epic, Cerner), AI diagnostics, patient portal management, remote monitoring
**Clinical Skills**: Evidence-based practice, patient safety protocols, quality improvement, clinical documentation, interdisciplinary collaboration
**Technology Systems**: Epic, Cerner, MEDITECH, HL7/FHIR standards, medical device integration, healthcare analytics
**Regulatory Compliance**: HIPAA, Joint Commission, CMS guidelines, FDA regulations, infection control, quality assurance
**Key Metrics**: Patient satisfaction scores, readmission rates, clinical outcomes, safety indicators, efficiency improvements
**Modern Focus**: Patient-centered care, population health, value-based care, care coordination, health equity""",

        "education": f"""

## EDUCATION INDUSTRY OPTIMIZATION ({current_year})
**Educational Technology**: Learning Management Systems (Canvas, Blackboard), virtual classroom tools, educational apps, adaptive learning platforms
**Modern Pedagogy**: Blended learning, competency-based education, differentiated instruction, social-emotional learning, culturally responsive teaching
**Assessment & Analytics**: Formative assessment, data-driven instruction, learning analytics, student progress monitoring, standardized test preparation
**Digital Literacy**: Online course design, multimedia content creation, digital citizenship, remote learning strategies
**Key Metrics**: Student achievement gains, engagement rates, graduation rates, assessment scores, professional development hours
**Current Trends**: Personalized learning, STEM/STEAM integration, project-based learning, trauma-informed practices""",

        "retail": f"""

## RETAIL INDUSTRY OPTIMIZATION ({current_year})
**Omnichannel Excellence**: E-commerce integration, mobile commerce, social commerce, buy-online-pick-up-in-store (BOPIS), curbside delivery
**Customer Experience**: Personalization, customer journey mapping, loyalty programs, customer service excellence, visual merchandising
**Technology Systems**: POS systems, inventory management, CRM platforms, analytics tools, mobile apps, payment processing
**Digital Marketing**: Social media marketing, influencer partnerships, email marketing, search engine optimization, content marketing
**Key Metrics**: Sales conversion rates, average transaction value, customer lifetime value, inventory turnover, profit margins
**Modern Trends**: Sustainable retail practices, experiential retail, artificial intelligence in retail, supply chain optimization""",

        "human_resources": f"""

## HUMAN RESOURCES OPTIMIZATION ({current_year})
**People Analytics**: HR metrics, predictive analytics, workforce planning, diversity analytics, employee lifecycle analysis
**Modern HR Tech**: HRIS systems (Workday, BambooHR), ATS platforms, employee engagement tools, performance management systems, AI recruitment
**Talent Management**: Talent acquisition, onboarding optimization, learning and development, succession planning, retention strategies
**Workplace Culture**: DEI initiatives, employee experience, remote work strategies, mental health support, flexible work arrangements
**Key Metrics**: Employee retention rates, time-to-hire, employee engagement scores, training effectiveness, diversity metrics
**Compliance**: Employment law, workplace safety (OSHA), benefits administration, compensation analysis, labor relations""",

        "sales": f"""

## SALES INDUSTRY OPTIMIZATION ({current_year})
**Modern Sales Techniques**: Social selling, consultative selling, account-based selling, inside sales, video prospecting, sales automation
**Technology Mastery**: CRM systems (Salesforce, HubSpot), sales enablement tools, lead generation platforms, sales analytics, pipeline management
**Digital Presence**: LinkedIn optimization, personal branding, content marketing, referral programs, networking strategies
**Performance Metrics**: Quota attainment, pipeline generation, deal size growth, sales cycle reduction, customer acquisition cost
**Key Skills**: Relationship building, negotiation, presentation skills, objection handling, territory management, upselling/cross-selling
**Modern Trends**: Revenue operations, sales and marketing alignment, customer success integration, data-driven selling""",

        "project_management": f"""

## PROJECT MANAGEMENT OPTIMIZATION ({current_year})
**Methodologies**: Agile/Scrum, Waterfall, Hybrid approaches, Lean, Kanban, Design Thinking, DevOps integration
**Technology Tools**: Jira, Asana, Monday.com, Microsoft Project, Slack, Confluence, Gantt charts, resource management tools
**Leadership Skills**: Stakeholder management, team leadership, conflict resolution, change management, risk management, communication
**Modern Practices**: Remote team management, cross-functional collaboration, continuous improvement, data-driven decision making
**Key Metrics**: On-time delivery, budget adherence, scope management, resource utilization, stakeholder satisfaction, ROI
**Certifications**: PMP, Scrum Master, SAFe, PRINCE2, Lean Six Sigma, change management""",

        "engineering": f"""

## ENGINEERING INDUSTRY OPTIMIZATION ({current_year})
**Digital Transformation**: CAD/CAM software, simulation tools, 3D printing, IoT integration, digital twins, automation systems
**Modern Practices**: Systems engineering, design thinking, lean manufacturing, sustainability engineering, quality assurance
**Technical Skills**: AutoCAD, SolidWorks, MATLAB, Python, data analysis, regulatory compliance, project management
**Industry 4.0**: Smart manufacturing, predictive maintenance, robotics, AI in engineering, supply chain optimization
**Key Metrics**: Design efficiency, cost reduction, quality improvements, safety incidents, project completion rates
**Specializations**: Mechanical, electrical, civil, chemical, software, environmental, biomedical engineering focus""",

        "legal": f"""

## LEGAL INDUSTRY OPTIMIZATION ({current_year})
**Legal Technology**: Document automation, e-discovery, legal research platforms (Westlaw, LexisNexis), case management systems, AI legal tools
**Modern Practice**: Remote hearings, digital document review, contract automation, compliance technology, legal analytics
**Core Competencies**: Legal research, writing, case analysis, client counseling, negotiation, litigation support, regulatory compliance
**Specialization Areas**: Corporate law, intellectual property, employment law, real estate, family law, criminal law, regulatory affairs
**Key Metrics**: Case success rates, client satisfaction, billing efficiency, document review speed, compliance rates
**Industry Trends**: Legal ops, alternative legal service providers, legal project management, data privacy law""",

        "real_estate": f"""

## REAL ESTATE INDUSTRY OPTIMIZATION ({current_year})
**Technology Integration**: CRM systems, virtual tour technology, drone photography, market analytics, digital marketing platforms
**Market Analysis**: Comparative market analysis, property valuation, market trends, investment analysis, demographic research
**Client Services**: Buyer/seller representation, negotiation, contract management, closing coordination, property management
**Digital Marketing**: Social media marketing, online listings, virtual staging, content marketing, lead generation
**Key Metrics**: Sales volume, commission rates, client satisfaction, days on market, listing-to-sale ratio
**Modern Trends**: PropTech innovation, sustainable building practices, remote closings, investment property focus"""
    }

    industry_key = industry.lower()
    if industry_key in industry_prompts:
        base_prompt += industry_prompts[industry_key]

    # Add tone-specific instructions
    tone_instructions = {
        "professional": "Use formal, industry-standard language. Focus on concrete achievements and maintain polished presentation.",
        "confident": "Use strong action verbs (Led, Transformed, Delivered, Achieved). Lead with major accomplishments and show decisiveness.",
        "creative": "Highlight innovative problem-solving and unique approaches. Emphasize creative projects and unconventional achievements.",
        "achievement": "Every statement must include quantifiable results. Lead with outcomes, use specific metrics and percentages."
    }

    if tone.lower() in tone_instructions:
        base_prompt += f"""

## TONE GUIDELINES: {tone.upper()}
{tone_instructions[tone.lower()]}"""

    # Add keyword optimization
    if focus_keywords:
        base_prompt += f"""

## KEYWORD INTEGRATION STRATEGY
Target Keywords: {focus_keywords}
- Integrate keywords naturally throughout professional summary, core competencies, and experience descriptions
- Prioritize keywords in context of actual achievements and responsibilities
- Ensure keyword density feels organic and readable
- Use variations and synonyms of key terms"""

    # Add current market insights
    base_prompt += f"""

## {current_year} HIRING MARKET INSIGHTS
**Remote/Hybrid Readiness**: Emphasize virtual collaboration, self-direction, and digital communication skills
**AI Integration**: Show adaptability to AI tools and automation (without overstating capabilities)
**Sustainability Focus**: Highlight ESG initiatives, sustainable practices, and environmental consciousness
**Inclusive Leadership**: Emphasize diverse team management, cultural competency, and inclusive practices
**Continuous Learning**: Show recent upskilling, certification pursuit, and industry trend awareness
**Soft Skills Priority**: Communication, emotional intelligence, adaptability, and critical thinking

## ATS OPTIMIZATION CHECKLIST
✅ Use standard section headers and clear hierarchy
✅ Include relevant keywords in context throughout content
✅ Use consistent date formats (MM/YYYY)
✅ Spell out acronyms on first use, then abbreviate
✅ Balance technical and soft skills appropriately
✅ Ensure 11-12 point readable font equivalent
✅ Avoid graphics, tables, headers/footers in content

## QUALITY STANDARDS
- Each achievement MUST include specific metrics or outcomes
- Professional summary should immediately convey unique value proposition
- Core competencies should align with target role requirements
- Experience descriptions should show progression and impact
- Overall narrative should be cohesive and compelling

Remember: You're creating a strategic marketing document that positions the candidate as the solution to the employer's specific needs. Every word should serve this purpose."""

    return base_prompt

def _post_process_resume_content(resume_content: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Post-process and validate the generated resume content with enhanced quality checks"""
    
    # Ensure all required sections are present
    required_sections = ["professional_summary", "core_competencies", "professional_experience", "education"]
    for section in required_sections:
        if section not in resume_content:
            if section == "professional_experience":
                resume_content[section] = []
            elif section == "core_competencies":
                resume_content[section] = profile_data.get("skills", [])[:10]
            elif section == "professional_summary":
                resume_content[section] = "Experienced professional with a strong background in " + profile_data.get("industry", "their field")
            else:
                resume_content[section] = []
    
    # Validate and enhance professional summary
    if isinstance(resume_content.get("professional_summary"), str):
        summary = resume_content["professional_summary"].strip()
        # Ensure summary is appropriately sized (50-100 words)
        words = summary.split()
        if len(words) > 100:
            resume_content["professional_summary"] = " ".join(words[:100])
        elif len(words) < 20:
            # Enhance too-short summary
            industry = profile_data.get("industry", "professional")
            resume_content["professional_summary"] = f"Results-driven {industry} professional with proven expertise in delivering measurable business outcomes. {summary}"
    
    # Validate core competencies
    if "core_competencies" in resume_content:
        competencies = resume_content["core_competencies"]
        if isinstance(competencies, list):
            # Clean and limit competencies
            clean_competencies = [comp.strip() for comp in competencies if comp.strip()]
            resume_content["core_competencies"] = clean_competencies[:12]
    
    # Validate experience section
    if "professional_experience" in resume_content:
        for i, exp in enumerate(resume_content["professional_experience"]):
            # Ensure required fields
            if "key_achievements" not in exp:
                exp["key_achievements"] = ["Contributed to team objectives and organizational goals"]
            
            # Validate achievements
            achievements = exp.get("key_achievements", [])
            if len(achievements) > 6:
                exp["key_achievements"] = achievements[:6]
            elif len(achievements) < 2:
                # Add generic achievement if too few
                exp["key_achievements"].append("Collaborated effectively with cross-functional teams to deliver project objectives")
            
            # Ensure employment period format
            if "employment_period" not in exp:
                exp["employment_period"] = "Employment period not specified"
    
    # Validate technical skills structure
    if "technical_skills" in resume_content and isinstance(resume_content["technical_skills"], dict):
        tech_skills = resume_content["technical_skills"]
        # Ensure all skill categories are lists
        for category in tech_skills:
            if not isinstance(tech_skills[category], list):
                tech_skills[category] = []
    
    # Add generation metadata
    resume_content["_metadata"] = {
        "generated_by": "deepseek",
        "generation_timestamp": datetime.now().isoformat(),
        "ats_optimized": True,
        "industry_tailored": True,
        "version": "2.0"
    }
    
    return resume_content

def get_industry_skills(industry: str) -> List[str]:
    """Get current, relevant skills for specific industries"""
    
    current_skills = {
        "technology": [
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "AWS", "Docker", "Kubernetes",
            "Git", "Agile/Scrum", "RESTful APIs", "GraphQL", "Microservices", "CI/CD", "DevOps", "AI/ML"
        ],
        "cybersecurity": [
            "SIEM/SOAR", "Zero Trust", "Cloud Security", "Penetration Testing", "Incident Response",
            "Risk Assessment", "Compliance", "Network Security", "DevSecOps", "Threat Intelligence",
            "Identity Management", "Vulnerability Management"
        ],
        "data_science": [
            "Python", "R", "SQL", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
            "Pandas", "NumPy", "Scikit-learn", "MLOps", "Apache Spark", "Tableau", "Power BI",
            "Statistical Analysis", "A/B Testing"
        ],
        "finance": [
            "Financial Modeling", "Excel", "SQL", "Python", "R", "Bloomberg Terminal", "FactSet",
            "Risk Management", "Financial Analysis", "Quantitative Analysis", "Regulatory Compliance",
            "ESG Reporting", "Fintech", "VBA"
        ],
        "marketing": [
            "Google Analytics", "SEO/SEM", "Social Media Marketing", "Content Strategy",
            "Marketing Automation", "HubSpot", "Salesforce", "A/B Testing", "Customer Analytics",
            "Performance Marketing", "CRM", "Email Marketing", "Adobe Creative Suite"
        ],
        "product_management": [
            "Product Strategy", "Roadmap Planning", "User Research", "A/B Testing", "Analytics",
            "Agile/Scrum", "Jira", "Figma", "SQL", "Data Analysis", "Stakeholder Management",
            "Go-to-Market Strategy", "Product-Led Growth"
        ],
        "customer_service": [
            "Customer Relationship Management", "Zendesk", "Salesforce Service Cloud", "Live Chat",
            "Conflict Resolution", "Active Listening", "Empathy", "Multilingual Communication",
            "Phone Etiquette", "Email Support", "Social Media Support", "Ticketing Systems",
            "Knowledge Base Management", "De-escalation Techniques"
        ],
        "healthcare": [
            "Electronic Health Records (EHR)", "Epic", "Cerner", "HIPAA Compliance", "Patient Care",
            "Medical Documentation", "Clinical Assessment", "Infection Control", "Patient Safety",
            "Telemedicine", "Medical Terminology", "CPR/BLS", "Healthcare Analytics", "Quality Improvement"
        ],
        "education": [
            "Curriculum Development", "Lesson Planning", "Classroom Management", "Learning Management Systems",
            "Educational Technology", "Student Assessment", "Differentiated Instruction", "IEP Development",
            "Canvas", "Blackboard", "Google Classroom", "Data-Driven Instruction", "Parent Communication"
        ],
        "retail": [
            "Point of Sale (POS)", "Inventory Management", "Customer Service", "Visual Merchandising",
            "Sales Techniques", "Product Knowledge", "Cash Handling", "Team Leadership",
            "E-commerce", "Social Media Marketing", "Customer Analytics", "Supply Chain Management"
        ],
        "human_resources": [
            "Talent Acquisition", "Employee Relations", "HRIS Systems", "Workday", "BambooHR",
            "Performance Management", "Compensation Analysis", "Benefits Administration", "Training & Development",
            "Employment Law", "DEI Initiatives", "Conflict Resolution", "Organizational Development"
        ],
        "sales": [
            "Salesforce CRM", "Lead Generation", "Pipeline Management", "Negotiation", "Cold Calling",
            "Social Selling", "Account Management", "Relationship Building", "Sales Forecasting",
            "Product Demonstrations", "Objection Handling", "Territory Management", "B2B Sales", "B2C Sales"
        ],
        "project_management": [
            "Project Planning", "Agile/Scrum", "Risk Management", "Stakeholder Management", "Jira",
            "Microsoft Project", "Asana", "Monday.com", "Budget Management", "Resource Allocation",
            "Team Leadership", "Change Management", "Quality Assurance", "PMP Certification"
        ],
        "engineering": [
            "AutoCAD", "SolidWorks", "MATLAB", "Project Management", "Quality Control", "Problem Solving",
            "Technical Documentation", "Safety Protocols", "Lean Manufacturing", "Six Sigma",
            "Python", "Data Analysis", "Regulatory Compliance", "Design Optimization"
        ],
        "legal": [
            "Legal Research", "Contract Review", "Legal Writing", "Case Management", "Westlaw",
            "LexisNexis", "Litigation Support", "Regulatory Compliance", "Document Review",
            "Client Counseling", "Negotiation", "Discovery Process", "Legal Analysis", "Court Procedures"
        ],
        "real_estate": [
            "Market Analysis", "Property Valuation", "Contract Negotiation", "MLS Systems", "Customer Service",
            "Sales Techniques", "Real Estate Law", "Property Management", "Investment Analysis",
            "Digital Marketing", "CRM Systems", "Photography", "Virtual Tours", "Lead Generation"
        ]
    }
    
    return current_skills.get(industry.lower().replace(" ", "_"), [])