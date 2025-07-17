// utils/resumeHelpers.js
import { capitalize } from "@/utils/formatters";

export const formatFormData = (form) => {
  form.fullName = capitalize(form.fullName);
  form.location = capitalize(form.location);
  form.title = form.title.trim();
  form.targetJobTitle = form.targetJobTitle.trim();
  form.targetJobRole = form.targetJobRole.trim();
  form.targetCompany = form.targetCompany.trim();
  form.summary = form.summary.trim();

  form.skills = form.skills.filter((s) => s.trim());
  if (form.includeCertifications) {
    form.certifications = form.certifications.filter((c) => c.trim());
  }
  if (form.includeLanguages) {
    form.languages = form.languages.filter((l) => l.trim());
  }

  form.workExperience.forEach((job) => {
    job.title = capitalize(job.title);
    job.company = capitalize(job.company);
    job.location = capitalize(job.location);
  });

  form.education.forEach((edu) => {
    edu.degree = capitalize(edu.degree);
    edu.school = capitalize(edu.school);
    edu.location = capitalize(edu.location);
  });

  if (form.includeProjects) {
    form.projects.forEach((project) => {
      project.title = capitalize(project.title);
      project.highlights = project.highlights.filter((h) => h.trim());
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
