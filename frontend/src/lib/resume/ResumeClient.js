import axios from "axios";
import { API_BASE_URL } from "@/utils/api";
import { getFirebaseAuth } from "@/utils/firebase";

function cleanObject(obj) {
  return Object.fromEntries(
    Object.entries(obj)
      .filter(([_, v]) =>
        v !== null && v !== undefined && (typeof v !== "string" || v.trim() !== "")
      )
  );
}

class ResumeClient {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api/v1/resume`
    });
  }

  getAuth() {
    return getFirebaseAuth();
  }

  async getAuthHeaders() {
    const auth = this.getAuth();
    const user = auth.currentUser;
    if (!user) throw new Error("User not authenticated");

    const idToken = await user.getIdToken();
    return {
      Authorization: `Bearer ${idToken}`,
      "Content-Type": "application/json"
    };
  }

  async generateResume(resumeData) {
    const headers = await this.getAuthHeaders();
    const res = await this.api.post("/", resumeData, { headers });
    return res.data;
  }

  async getResume(id) {
    const headers = await this.getAuthHeaders();
    const res = await this.api.get(`/${id}`, { headers });
    return res.data;
  }

  async updateResume(id, resumeData) {
    const headers = await this.getAuthHeaders();

    const profile = resumeData.profile || {};

    const updatePayload = {
      title: resumeData.title,
      target_job_title: resumeData.targetJobTitle,
      target_job_role: resumeData.targetJobRole,
      target_company: resumeData.targetCompany,
      ai_tone: resumeData.aiTone || resumeData.tone,
      ai_length: resumeData.aiLength || resumeData.length,
      template_id: resumeData.templateId || resumeData.template_id,
      focus_keywords: resumeData.focusKeywords || resumeData.focus_keywords,
      include_projects: resumeData.includeProjects,
      include_certifications: resumeData.includeCertifications,
      include_languages: resumeData.includeLanguages,
      use_ai: resumeData.useAI,
      custom_sections: resumeData.custom_sections,
      profile_data: cleanObject({
        full_name: resumeData.fullName || profile.fullName,
        email: (resumeData.email || profile.email)?.trim() || null,
        phone: (resumeData.phone || profile.phone)?.trim() || null,
        linkedin: (resumeData.linkedin || profile.linkedin)?.trim() || null,
        location: (resumeData.location || profile.location)?.trim() || null,
        industry: resumeData.industry || profile.industry,
        summary: (resumeData.summary || profile.summary)?.trim() || null,
        skills: resumeData.skills || profile.skills || [],
        certifications: (resumeData.certifications || profile.certifications || []).map(cert => {
          if (typeof cert === 'string') return cert;
          return {
            name: cert.name || '',
            issuer: cert.issuer || '',
            date: cert.date || ''
          };
        }).filter(cert => typeof cert === 'string' ? cert.trim() : cert.name?.trim()),
        work_experience: (resumeData.workExperience || profile.workExperience || []).map(exp => ({
          title: exp.title || "",
          company: exp.company || "",
          location: exp.location || "",
          start_date: exp.startDate || "",
          end_date: exp.endDate || "",
          current: !exp.endDate,
          description: exp.description || "",
          highlights: exp.highlights || []
        })),
        education: (resumeData.education || profile.education || []).map(edu => ({
          degree: edu.degree || "",
          school: edu.school || "",
          location: edu.location || "",
          graduation_date: edu.graduationDate || "",
          description: edu.description || "",
          gpa: edu.gpa || ""
        })),
        projects: (resumeData.projects || profile.projects || []).map(project => ({
          title: project.title || "",
          description: project.description || "",
          technologies: project.technologies || [],
          url: project.url || "",
          start_date: project.startDate || "",
          end_date: project.endDate || "",
          highlights: project.highlights || []
        })),
        languages: (resumeData.languages || profile.languages || []).map(lang => {
          if (typeof lang === 'string') {
            return { language: lang, proficiency: 'conversational' };
          }
          return {
            language: lang.name || lang.language || '',
            proficiency: lang.proficiency || lang.level || 'conversational'
          };
        })
      })
    };

    const cleanedPayload = cleanObject(updatePayload);

    console.log('Update payload:', JSON.stringify(cleanedPayload, null, 2));

    try {
      const res = await this.api.put(`/${id}`, cleanedPayload, { headers });
      return res.data;
    } catch (error) {
      console.error('Update resume error:', error);
      if (error.response) {
        console.error('Backend response:', error.response.data);
      }
      throw new Error(error.response?.data?.detail || "Resume update failed");
    }
  }

  async deleteResume(id) {
    const headers = await this.getAuthHeaders();
    const res = await this.api.delete(`/${id}`, { headers });
    return res.data;
  }

  async restoreResume(id) {
    const headers = await this.getAuthHeaders();
    const res = await this.api.post(`/${id}/restore`, {}, { headers });
    return res.data;
  }

  async listResumes({ page = 1, perPage = 10, search = "", industry = "", template = "", sortBy = "created_at", sortOrder = "desc" } = {}) {
    const headers = await this.getAuthHeaders();
    const res = await this.api.get("/", {
      headers,
      params: {
        page,
        per_page: perPage,
        search,
        industry,
        template,
        sort_by: sortBy,
        sort_order: sortOrder
      }
    });
    return res.data;
  }

  async getUserResumes(params = {}) {
    return await this.listResumes(params);
  }

  async downloadResume(id, format = 'pdf') {
    const headers = await this.getAuthHeaders();
    const res = await this.api.get(`/${id}/download`, {
      headers,
      params: { format },
      responseType: 'blob'
    });
    return {
      blob: res.data,
      filename: res.headers['content-disposition']?.split('filename=')[1] || `resume.${format}`
    };
  }

  async duplicateResume(id) {
    const headers = await this.getAuthHeaders();
    const res = await this.api.post(`/${id}/duplicate`, {}, { headers });
    return res.data;
  }

  async shareResume(id) {
    const headers = await this.getAuthHeaders();
    const res = await this.api.post(`/${id}/share`, {}, { headers });
    return res.data;
  }

  async regenerateContent(id) {
    const headers = await this.getAuthHeaders();
    const res = await this.api.post(`/${id}/regenerate`, {}, { headers });
    return res.data;
  }
}

export const resumeClient = new ResumeClient();
export default resumeClient;
