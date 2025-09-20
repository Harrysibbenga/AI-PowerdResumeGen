// utils/resumeHelpers.js
import { capitalize } from "@/utils/formatters";

export const formatFormData = (form) => {
  // Basic personal info formatting
  form.fullName = capitalize(form.fullName);
  form.location = capitalize(form.location);
  form.title = form.title.trim();
  form.targetJobTitle = form.targetJobTitle.trim();
  form.targetJobRole = form.targetJobRole.trim();
  form.targetCompany = form.targetCompany.trim();
  form.summary = form.summary.trim();
  form.skills = form.skills.filter((s) => s.trim());

  // Work experience formatting
  form.workExperience.forEach((job) => {
    job.title = capitalize(job.title);
    job.company = capitalize(job.company);
    job.location = capitalize(job.location);
  });

  // Education formatting
  form.education.forEach((edu) => {
    edu.degree = capitalize(edu.degree);
    edu.school = capitalize(edu.school);
    edu.location = capitalize(edu.location);
  });

  // Projects formatting - updated for new structure
  if (form.includeProjects && form.projects) {
    form.projects.forEach((project) => {
      project.title = capitalize(project.title);
      // Filter out empty highlights
      project.highlights = project.highlights.filter((h) => h.trim());
      // Ensure technologies array exists and is cleaned
      if (project.technologies) {
        project.technologies = project.technologies.filter((tech) => tech.trim());
      }
      // Clean URL and description
      if (project.url) {
        project.url = project.url.trim();
      }
      if (project.description) {
        project.description = project.description.trim();
      }
    });
  }

  // Certifications formatting
  if (form.includeCertifications && form.certifications) {
    form.certifications = form.certifications.filter((c) => c.trim());
  }
  
  // Languages formatting - updated for new structure
  if (form.includeLanguages && form.languages) {
    form.languages = form.languages.filter((lang) => {
      // Handle both old string format and new object format
      if (typeof lang === 'string') {
        return lang.trim();
      } else if (typeof lang === 'object' && lang.language && lang.proficiency) {
        // Clean the language and proficiency fields
        lang.language = capitalize(lang.language.trim());
        lang.proficiency = lang.proficiency.trim();
        return lang.language && lang.proficiency;
      }
      return false;
    });
  }
};

export const generateAutoSummary = (form) => {
  if (form.summary.trim()) return form.summary;

  const experience = form.workExperience.filter((exp) => exp.title && exp.company);
  const skills = form.skills.filter((skill) => skill.trim());
  const yearsExp = experience.length > 0 ? `${experience.length}+ years of` : "";
  const role = form.targetJobTitle || form.industry || "professional";

  return `${yearsExp} experience as a ${role} with expertise in ${skills
    .slice(0, 3)
    .join(", ")}. Proven track record of delivering results and driving growth.`;
};

// Helper function to convert old language format to new format
export const migrateLanguagesFormat = (languages) => {
  if (!languages || !Array.isArray(languages)) return [];
  
  return languages.map(lang => {
    if (typeof lang === 'string') {
      // Try to parse old format: "Spanish (Fluent)"
      const match = lang.match(/^(.+?)\s*\((.+?)\)$/);
      if (match) {
        return {
          language: match[1].trim(),
          proficiency: match[2].trim()
        };
      } else {
        // Fallback for languages without proficiency
        return {
          language: lang.trim(),
          proficiency: 'Intermediate'
        };
      }
    } else if (typeof lang === 'object' && lang.language && lang.proficiency) {
      // Already in new format
      return lang;
    }
    return null;
  }).filter(Boolean);
};

// Helper function to format languages for display (backwards compatibility)
export const formatLanguageForDisplay = (language) => {
  if (typeof language === 'string') {
    return language;
  } else if (typeof language === 'object' && language.language && language.proficiency) {
    return `${language.language} (${language.proficiency})`;
  }
  return '';
};

// Helper function to get all technologies from projects
export const getAllTechnologies = (projects) => {
  if (!projects || !Array.isArray(projects)) return [];
  
  const allTech = [];
  projects.forEach(project => {
    if (project.technologies && Array.isArray(project.technologies)) {
      allTech.push(...project.technologies);
    }
  });
  
  // Remove duplicates and return sorted array
  return [...new Set(allTech)].sort();
};

// Helper function to validate project data
export const validateProject = (project) => {
  const errors = [];
  
  if (!project.title || !project.title.trim()) {
    errors.push('Project title is required');
  }
  
  if (!project.description || !project.description.trim()) {
    errors.push('Project description is required');
  }
  
  if (project.url && project.url.trim()) {
    try {
      new URL(project.url);
    } catch {
      errors.push('Project URL must be a valid URL');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// Helper function to validate language data
export const validateLanguage = (language) => {
  if (typeof language === 'string') {
    return {
      isValid: language.trim().length > 0,
      errors: language.trim().length > 0 ? [] : ['Language cannot be empty']
    };
  }
  
  if (typeof language === 'object') {
    const errors = [];
    
    if (!language.language || !language.language.trim()) {
      errors.push('Language name is required');
    }
    
    if (!language.proficiency || !language.proficiency.trim()) {
      errors.push('Proficiency level is required');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
  
  return {
    isValid: false,
    errors: ['Invalid language format']
  };
};