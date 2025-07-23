// composables/useResumeForm.js
import { ref } from "vue";

export const useResumeForm = () => {
  const form = ref({
    title: "",
    targetJobTitle: "",
    targetJobRole: "",
    targetCompany: "",
    summary: "",
    fullName: "",
    email: "",
    phone: "",
    linkedin: "",
    location: "",
    website: "",
    github: "",
    industry: "",
    skills: [""],
    certifications: [""],
    languages: [""],
    workExperience: [
      {
        title: "",
        company: "",
        location: "",
        startDate: "",
        endDate: "",
        description: "",
      },
    ],
    education: [
      {
        degree: "",
        school: "",
        location: "",
        graduationDate: "",
        description: "",
      },
    ],
    projects: [
      {
        title: "",
        description: "",
        technologies: [],
        url: "",
        startDate: "",
        endDate: "",
        highlights: [""],
      },
    ],
    tone: "professional",
    length: "standard",
    templateId: "modern",
    focusKeywords: "",
    includeProjects: true,
    includeCertifications: true,
    includeLanguages: true,
  });

  return { form };
};
