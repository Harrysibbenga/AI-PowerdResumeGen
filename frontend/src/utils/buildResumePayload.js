// utils/buildResumePayload.js
export const buildResumePayload = (form) => ({
  // Resume metadata
  title: form.title,
  targetJobTitle: form.targetJobTitle,
  targetJobRole: form.targetJobRole || null,
  targetCompany: form.targetCompany || null,
  
  // AI settings
  aiTone: form.aiTone || 'professional',
  aiLength: form.aiLength || 'standard',
  template_id: form.templateId || 'modern',
  focusKeywords: form.focusKeywords || null,
  useAI: form.useAI !== undefined ? form.useAI : true,
  
  // Section inclusion flags
  includeProjects: form.includeProjects,
  includeCertifications: form.includeCertifications,
  includeLanguages: form.includeLanguages,
  
  // Custom sections
  custom_sections: form.customSections || null,
  
  // Profile data
  profile: {
    // Personal info
    fullName: form.fullName,
    email: form.email,
    phone: form.phone || null,
    linkedin: form.linkedin || null,
    location: form.location || null,
    
    // Professional details
    summary: form.summary || null,
    industry: form.industry,
    skills: form.skills || [],
    certifications: form.includeCertifications ? (form.certifications || []) : [],
    languages: form.includeLanguages ? formatLanguagesForBackend(form.languages || []) : [],
    
    // Work experience
    workExperience: (form.workExperience || [])
      .filter((exp) => exp.title && exp.company)
      .map((exp) => ({
        title: exp.title,
        company: exp.company,
        location: exp.location || null,
        startDate: exp.startDate,
        endDate: exp.endDate || null,
        description: exp.description,
        current: !exp.endDate,
        highlights: exp.highlights ? exp.highlights.filter(h => h.trim()) : []
      })),
    
    // Education
    education: (form.education || [])
      .filter((edu) => edu.degree && edu.school)
      .map((edu) => ({
        degree: edu.degree,
        school: edu.school,
        location: edu.location || null,
        graduationDate: edu.graduationDate,
        description: edu.description || null,
        gpa: edu.gpa || null
      })),
    
    // Projects
    projects: form.includeProjects
      ? (form.projects || [])
          .filter((p) => p.title && p.description)
          .map((project) => ({
            title: project.title,
            description: project.description,
            technologies: project.technologies || [],
            url: project.url || null,
            startDate: project.startDate || null,
            endDate: project.endDate || null,
            highlights: project.highlights ? project.highlights.filter(h => h.trim()) : []
          }))
      : [],
  },
});

// Helper function to format languages for backend
const formatLanguagesForBackend = (languages) => {
  if (!languages || !Array.isArray(languages)) return [];
  
  return languages.map(lang => {
    // Handle new object format
    if (typeof lang === 'object' && lang.language && lang.proficiency) {
      return {
        language: lang.language,
        proficiency: lang.proficiency
      };
    }
    
    // Handle old string format for migration
    if (typeof lang === 'string') {
      const match = lang.match(/^(.+?)\s*\((.+?)\)$/);
      if (match) {
        return {
          language: match[1].trim(),
          proficiency: match[2].trim()
        };
      } else {
        return {
          language: lang.trim(),
          proficiency: 'Intermediate'
        };
      }
    }
    
    return null;
  }).filter(Boolean);
};