<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-6xl mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button
              @click="goBack"
              class="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
                  clip-rule="evenodd"
                ></path>
              </svg>
              Back to Dashboard
            </button>
          </div>

          <!-- Action Buttons -->
          <ResumeActions
            :regenerating="regenerating"
            :exporting="exporting"
            :show-export-menu="showExportMenu"
            @regenerate="regenerateContent"
            @print="printResume"
            @edit="editResume"
            @export="exportResume"
            @toggle-export="toggleExportMenu"
            ref="exportDropdown"
          />
        </div>

        <!-- Resume Metadata -->
        <ResumeMetadata :metadata="resumeMetadata" />
      </div>
    </div>

    <div class="max-w-4xl mx-auto p-6">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"
        ></div>
        <p class="text-gray-600">Loading resume...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <div class="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
          <svg
            class="w-12 h-12 text-red-400 mx-auto mb-4"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clip-rule="evenodd"
            ></path>
          </svg>
          <h2 class="text-xl font-semibold text-red-800 mb-2">Failed to Load Resume</h2>
          <p class="text-red-600 mb-4">{{ error }}</p>
          <button
            @click="loadResume"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Resume Content -->
      <div v-else class="bg-white shadow-lg rounded-lg overflow-hidden">
        <!-- Header Section -->
        <ResumeHeader :personal-info="getPersonalInfo()" />

        <div class="p-8">
          <!-- Professional Summary -->
          <section v-if="getProfessionalSummary()" class="mb-8">
            <SectionHeader title="Professional Summary" />
            <div class="prose text-gray-700 leading-relaxed">
              <p>{{ getProfessionalSummary() }}</p>
            </div>
          </section>

          <!-- Core Competencies -->
          <section v-if="getCoreCompetencies()?.length" class="mb-8">
            <SectionHeader title="Core Competencies" />
            <div class="flex flex-wrap gap-2">
              <SkillPill
                v-for="(skill, index) in getCoreCompetencies()"
                :key="`competency-${index}`"
                :label="skill"
                variant="primary"
              />
            </div>
          </section>

          <!-- Professional Experience -->
          <section v-if="getWorkExperience()?.length" class="mb-8">
            <SectionHeader title="Professional Experience" />
            <div class="space-y-6">
              <ExperienceCard
                v-for="(exp, index) in getWorkExperience()"
                :key="`exp-${index}`"
                :experience="exp"
              />
            </div>
          </section>

          <!-- Technical Skills -->
          <section v-if="getTechnicalSkills()" class="mb-8">
            <SectionHeader title="Technical Skills" />
            <TechnicalSkillsSection :skills="getTechnicalSkills()" />
          </section>

          <!-- Education -->
          <section v-if="getEducation()?.length" class="mb-8">
            <SectionHeader title="Education" />
            <div class="space-y-4">
              <EducationCard
                v-for="(edu, index) in getEducation()"
                :key="`edu-${index}`"
                :education="edu"
              />
            </div>
          </section>

          <!-- Notable Projects -->
          <section v-if="getNotableProjects()?.length" class="mb-8">
            <SectionHeader title="Notable Projects" />
            <div class="space-y-6">
              <ProjectCard
                v-for="(project, index) in getNotableProjects()"
                :key="`project-${index}`"
                :project="project"
              />
            </div>
          </section>

          <!-- Certifications -->
          <section v-if="getCertifications()?.length" class="mb-8">
            <SectionHeader title="Certifications" />
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="(cert, index) in getCertifications()"
                :key="`cert-${index}`"
                class="flex items-center p-3 border border-gray-200 rounded-lg"
              >
                <svg
                  class="w-5 h-5 text-green-600 mr-3 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clip-rule="evenodd"
                  ></path>
                </svg>
                <span class="text-gray-900 font-medium">{{ cert }}</span>
              </div>
            </div>
          </section>

          <!-- Languages -->
          <section v-if="getLanguages()?.length" class="mb-8">
            <SectionHeader title="Languages" />
            <div class="flex flex-wrap gap-2">
              <SkillPill
                v-for="(language, index) in getLanguages()"
                :key="`lang-${index}`"
                :label="language.language"
                :sublabel="language.proficiency"
                variant="green"
              />
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";
import { usePrintResume } from "@/composables/usePrintResume";

// Import components
import SkillPill from "@/components/vue/ui/SkillPill.vue";
import SectionHeader from "@/components/vue/ui/SectionHeader.vue";
import ResumeHeader from "@/components/vue/resume/ResumeHeader.vue";
import ResumeMetadata from "@/components/vue/resume/ResumeMetadata.vue";
import ResumeActions from "@/components/vue/resume/ResumeActions.vue";
import ExperienceCard from "@/components/vue/resume/ExperienceCard.vue";
import ProjectCard from "@/components/vue/resume/ProjectCard.vue";
import EducationCard from "@/components/vue/resume/EducationCard.vue";
import TechnicalSkillsSection from "@/components/vue/resume/TechnicalSkillsSection.vue";

const props = defineProps({
  resumeId: {
    type: String,
    required: false,
  },
});

const resumeData = ref({
  sections: {},
  profile: {},
  ai_content: {},
  profile_data: {},
});

const resumeMetadata = ref(null);
const loading = ref(true);
const error = ref(null);
const exporting = ref(false);
const regenerating = ref(false);
const showExportMenu = ref(false);
const exportDropdown = ref(null);

const { waitForAuth } = useFirebase();
const { success, error: showError } = useToast();

const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

// Helper methods to extract data from multiple possible sources
const getPersonalInfo = () => {
  const aiContent = resumeData.value.ai_content || {};
  const profileData = resumeData.value.profile_data || {};
  const sections = resumeData.value.sections || {};

  return {
    name: profileData.fullName || sections.personal_info?.name || "John Doe",
    email:
      profileData.email ||
      sections.personal_info?.email ||
      sections.contact_info?.email ||
      "",
    phone:
      profileData.phone ||
      sections.personal_info?.phone ||
      sections.contact_info?.phone ||
      "",
    location:
      profileData.location ||
      sections.personal_info?.location ||
      sections.contact_info?.location ||
      "",
    linkedin:
      profileData.linkedin ||
      sections.personal_info?.linkedin ||
      sections.contact_info?.linkedin ||
      "",
  };
};

const getProfessionalSummary = () => {
  const aiContent = resumeData.value.ai_content || {};
  const profileData = resumeData.value.profile_data || {};
  const sections = resumeData.value.sections || {};

  return (
    aiContent.professional_summary ||
    profileData.summary ||
    sections.professional_summary ||
    sections.summary ||
    ""
  );
};

const getCoreCompetencies = () => {
  const aiContent = resumeData.value.ai_content || {};
  const profileData = resumeData.value.profile_data || {};
  const sections = resumeData.value.sections || {};

  return (
    aiContent.core_competencies ||
    profileData.skills ||
    sections.core_competencies ||
    sections.skills ||
    []
  );
};

const getWorkExperience = () => {
  const aiContent = resumeData.value.ai_content || {};
  const profileData = resumeData.value.profile_data || {};
  const sections = resumeData.value.sections || {};

  return (
    aiContent.professional_experience ||
    profileData.workExperience ||
    sections.experience ||
    sections.work_experience ||
    []
  );
};

const getTechnicalSkills = () => {
  const aiContent = resumeData.value.ai_content || {};
  const profileData = resumeData.value.profile_data || {};
  const sections = resumeData.value.sections || {};

  // If we have technical_skills object, return it
  if (aiContent.technical_skills || sections.technical_skills) {
    return aiContent.technical_skills || sections.technical_skills;
  }

  // Otherwise, try to construct from available skill data
  const skills = profileData.skills || sections.skills || [];
  const primaryTech = aiContent.technical_skills?.primary_technologies || [];
  const secondarySkills = aiContent.technical_skills?.secondary_skills || [];

  if (primaryTech.length || secondarySkills.length) {
    return {
      primary_technologies: primaryTech,
      secondary_skills: secondarySkills,
    };
  }

  // If we just have a flat array of skills, group them
  if (skills.length > 0) {
    return {
      technical_skills: skills,
    };
  }

  return null;
};

const getEducation = () => {
  const aiContent = resumeData.value.ai_content || {};
  const profileData = resumeData.value.profile_data || {};
  const sections = resumeData.value.sections || {};

  return aiContent.education || profileData.education || sections.education || [];
};

const getNotableProjects = () => {
  const aiContent = resumeData.value.ai_content || {};
  const profileData = resumeData.value.profile_data || {};
  const sections = resumeData.value.sections || {};

  return (
    aiContent.notable_projects ||
    profileData.projects ||
    sections.projects ||
    sections.notable_projects ||
    []
  );
};

const getCertifications = () => {
  const aiContent = resumeData.value.ai_content || {};
  const profileData = resumeData.value.profile_data || {};
  const sections = resumeData.value.sections || {};

  return (
    aiContent.technical_skills?.certifications ||
    profileData.certifications ||
    sections.certifications ||
    []
  );
};

const getLanguages = () => {
  const aiContent = resumeData.value.ai_content || {};
  const profileData = resumeData.value.profile_data || {};
  const sections = resumeData.value.sections || {};

  // Check all possible locations for languages data
  const languages =
    profileData.languages ||
    aiContent.languages ||
    sections.languages ||
    sections.additional_sections?.languages ||
    [];

  // Ensure we return an array of objects with language and proficiency
  if (Array.isArray(languages) && languages.length > 0) {
    // If it's already in the correct format
    if (typeof languages[0] === "object" && languages[0].language) {
      return languages;
    }
    // If it's just an array of strings, convert to object format
    if (typeof languages[0] === "string") {
      return languages.map((lang) => ({ language: lang, proficiency: "Proficient" }));
    }
  }

  return [];
};

const getResumeId = () => {
  return props.resumeId || new URLSearchParams(window.location.search).get("id");
};

const loadResume = async () => {
  const resumeId = getResumeId();

  if (!resumeId) {
    error.value = "No resume ID provided";
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    const user = await waitForAuth();
    if (!user) {
      showError("Please log in to view your resume");
      setTimeout(() => (window.location.href = "/login"), 1500);
      return;
    }

    const token = await user.getIdToken();
    const response = await fetch(`${API_URL}/api/v1/resume/${resumeId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error("Resume not found");
      } else if (response.status === 403) {
        throw new Error("You do not have permission to view this resume");
      } else {
        throw new Error(`Failed to load resume (${response.status})`);
      }
    }

    const data = await response.json();

    // Store all possible data sources with proper reactivity
    resumeData.value = {
      sections: data.sections || {},
      profile: data.profile || {},
      ai_content: data.ai_content || data.sections || {},
      profile_data: data.profile_data || {},
      rawData: data,
    };

    // Debug log to check languages data
    console.log("Languages data check:", {
      profileDataLanguages: data.profile_data?.languages,
      aiContentLanguages: data.ai_content?.languages,
      sectionsLanguages: data.sections?.languages,
      getLanguagesResult: getLanguages(),
    });

    resumeMetadata.value = {
      id: data.id,
      title: data.title,
      target_job_title: data.target_job_title,
      target_job_role: data.target_job_role,
      industry: data.industry,
      template_id: data.template_id,
      word_count: data.word_count,
      sections_count: data.sections_count,
      created_at: data.created_at,
      export_status: data.export_status,
    };
  } catch (err) {
    console.error("Error loading resume:", err);
    error.value = err.message || "Failed to load resume";
    showError(err.message || "Failed to load resume");
  } finally {
    loading.value = false;
  }
};

const exportResume = async (format) => {
  try {
    exporting.value = true;
    showExportMenu.value = false;

    const resumeId = getResumeId();
    const user = await waitForAuth();

    if (!user) {
      showError("Please log in to export your resume");
      return;
    }

    const token = await user.getIdToken();

    // Start export
    const exportResponse = await fetch(
      `${API_URL}/api/v1/resume/export/${resumeId}/export`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resumeId: resumeId,
          format: format,
          content: resumeData.value.ai_content || resumeData.value.sections,
        }),
      }
    );

    if (!exportResponse.ok) {
      const errorData = await exportResponse.json();
      if (errorData.message === "export_limit_reached") {
        showError(
          "You've reached your monthly export limit. Please upgrade to continue."
        );
        return;
      }
      throw new Error(errorData.message || "Failed to start export");
    }

    const exportData = await exportResponse.json();

    if (exportData.message === "export_limit_reached") {
      showError("You've reached your monthly export limit. Please upgrade to continue.");
      return;
    }

    // Poll for completion
    const pollInterval = setInterval(async () => {
      try {
        const statusResponse = await fetch(
          `${API_URL}/api/v1/resume/export/${exportData.download_url
            .split("/")
            .pop()}/status`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (statusResponse.ok) {
          const statusData = await statusResponse.json();

          if (statusData.status === "completed") {
            clearInterval(pollInterval);

            // Download the file
            const downloadResponse = await fetch(exportData.download_url, {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            });

            if (downloadResponse.ok) {
              const blob = await downloadResponse.blob();
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement("a");
              link.href = url;
              link.download = exportData.filename;
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              window.URL.revokeObjectURL(url);

              success(`Resume exported as ${format.toUpperCase()} successfully!`);
            }
          } else if (statusData.status === "failed") {
            clearInterval(pollInterval);
            throw new Error(statusData.error_message || "Export failed");
          }
        }
      } catch (err) {
        clearInterval(pollInterval);
        console.error("Error checking export status:", err);
        showError("Error during export process");
      }
    }, 2000);

    // Timeout after 2 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      if (exporting.value) {
        showError("Export is taking longer than expected. Please try again.");
        exporting.value = false;
      }
    }, 120000);
  } catch (err) {
    console.error("Error exporting resume:", err);
    showError(err.message || "Failed to export resume");
  } finally {
    exporting.value = false;
  }
};

const regenerateContent = async () => {
  try {
    regenerating.value = true;
    const resumeId = getResumeId();
    const user = await waitForAuth();

    if (!user) {
      showError("Please log in to regenerate content");
      return;
    }

    const token = await user.getIdToken();
    const response = await fetch(`${API_URL}/api/v1/resume/regenerate/${resumeId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to regenerate content");
    }

    const data = await response.json();

    // Update the resume data with new content
    resumeData.value.ai_content = data.ai_content || data.sections;
    resumeData.value.sections = data.sections || data.ai_content;
    success("Resume content regenerated successfully!");
  } catch (err) {
    console.error("Error regenerating content:", err);
    showError(err.message || "Failed to regenerate content");
  } finally {
    regenerating.value = false;
  }
};

const editResume = () => {
  const resumeId = getResumeId();
  window.location.href = `/builder?edit=${resumeId}`;
};

const goBack = () => {
  window.location.href = "/dashboard";
};

const toggleExportMenu = () => {
  showExportMenu.value = !showExportMenu.value;
};

// Click outside to close export menu
const handleClickOutside = (event) => {
  if (exportDropdown.value && !exportDropdown.value.contains(event.target)) {
    showExportMenu.value = false;
  }
};

const { printResume } = usePrintResume(resumeData.value);

// Initialize
onMounted(() => {
  loadResume();
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Print styles */
@media print {
  .bg-gradient-to-r {
    background: white !important;
  }

  .shadow-lg {
    box-shadow: none !important;
  }

  .border {
    border: 1px solid #e5e7eb !important;
  }
}
</style>
