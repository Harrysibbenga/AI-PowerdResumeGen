// utils/buildResumePayload.js
export const buildResumePayload = (form) => ({
  title: form.title,
  target_job_title: form.targetJobTitle,
  target_job_role: form.targetJobRole || null,
  target_company: form.targetCompany || null,
  tone: form.tone,
  length: form.length,
  template_id: form.templateId,
  focus_keywords: form.focusKeywords || null,
  include_projects: form.includeProjects,
  include_certifications: form.includeCertifications,
  include_languages: form.includeLanguages,
  profile: {
    name: form.fullName,
    email: form.email,
    phone: form.phone,
    linkedin: form.linkedin,
    location: form.location,
    website: form.website,
    github: form.github,
    professional_summary: form.summary,
    industry: form.industry,
    skills: form.skills,
    certifications: form.includeCertifications ? form.certifications : [],
    languages: form.includeLanguages ? form.languages : [],
    experience: form.workExperience
      .filter((exp) => exp.title && exp.company)
      .map((exp) => ({
        title: exp.title,
        company: exp.company,
        location: exp.location,
        startDate: exp.startDate,
        endDate: exp.endDate || null,
        description: exp.description,
        current: !exp.endDate,
      })),
    education: form.education
      .filter((edu) => edu.degree && edu.school)
      .map((edu) => ({
        degree: edu.degree,
        institution: edu.school,
        location: edu.location,
        startYear:
          parseInt(edu.graduationDate?.split("-")[0]) || new Date().getFullYear() - 4,
        endYear:
          parseInt(edu.graduationDate?.split("-")[0]) || new Date().getFullYear(),
        description: edu.description,
      })),
    projects: form.includeProjects
      ? form.projects.filter((p) => p.title && p.description)
      : [],
  },
});
