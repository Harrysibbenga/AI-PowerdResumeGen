<template>
  <form @submit.prevent="handleSubmit" class="space-y-8">
    <!-- Error Display -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-600 text-sm">{{ error }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"
      ></div>
      <p class="text-primary-600 font-medium">Generating your resume...</p>
      <p class="text-gray-500 text-sm mt-2">This may take a few moments</p>
    </div>

    <!-- Form Sections -->
    <div v-else class="space-y-8">
      <!-- Resume Title Section -->
      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Resume Details</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label for="resumeTitle" class="block text-sm font-medium text-gray-700 mb-2">
              Resume Title *
            </label>
            <input
              id="resumeTitle"
              v-model="form.title"
              type="text"
              placeholder="e.g., Senior Software Engineer Resume"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              required
            />
          </div>
          <div>
            <label for="targetRole" class="block text-sm font-medium text-gray-700 mb-2">
              Target Role
            </label>
            <input
              id="targetRole"
              v-model="form.targetRole"
              type="text"
              placeholder="e.g., Senior Software Engineer"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </div>

      <PersonalInfoSection v-model="form" />
      <IndustrySelector v-model="form.industry" @industryChanged="handleIndustryChange" />

      <!-- Professional Summary Section -->
      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Professional Summary</h3>
        <div>
          <label for="summary" class="block text-sm font-medium text-gray-700 mb-2">
            Professional Summary (Optional)
          </label>
          <textarea
            id="summary"
            v-model="form.summary"
            rows="4"
            placeholder="Brief overview of your professional background, key skills, and career objectives. Leave blank to auto-generate based on your experience."
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">
            If left blank, we'll generate a professional summary based on your experience
            and skills.
          </p>
        </div>
      </div>

      <SkillsInput v-model="form.skills" :industry="form.industry" />
      <CertificationsInput v-model="form.certifications" :industry="form.industry" />
      <WorkExperienceInput v-model="form.workExperience" />
      <EducationInput v-model="form.education" />

      <!-- Submit Button -->
      <div class="flex justify-center pt-6">
        <button
          type="submit"
          :disabled="loading || !isFormValid"
          class="px-8 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span class="flex items-center">
            <svg
              v-if="loading"
              class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            {{ loading ? "Generating Resume..." : "Generate Resume" }}
          </span>
        </button>
      </div>
    </div>
  </form>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";

import PersonalInfoSection from "./PersonalInfoSection.vue";
import IndustrySelector from "./IndustrySelector.vue";
import SkillsInput from "./SkillsInput.vue";
import CertificationsInput from "./CertificationsInput.vue";
import WorkExperienceInput from "./WorkExperienceInput.vue";
import EducationInput from "./EducationInput.vue";

import { capitalize } from "@/utils/formatters.js";
import { defaultForm } from "@/utils/defaultForm.js";

const loading = ref(false);
const error = ref("");
const form = ref({
  // Resume metadata
  title: "",
  targetRole: "",
  summary: "",

  // Personal info
  fullName: "",
  email: "",
  phone: "",
  linkedin: "",
  location: "",

  // Professional details
  industry: "",
  skills: [""],
  certifications: [""],

  // Experience and education
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
});

const { waitForAuth } = useFirebase();
const { success, error: showError } = useToast();

const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

// Computed properties
const isFormValid = computed(() => {
  return (
    form.value.title.trim() &&
    form.value.fullName.trim() &&
    form.value.email.trim() &&
    form.value.industry.trim()
  );
});

// Methods
const handleIndustryChange = () => {
  // Update target role suggestion based on industry
  if (form.value.industry && !form.value.targetRole) {
    // You can add logic here to suggest roles based on industry
  }
};

const formatFormData = () => {
  // Clean and format form data
  form.value.fullName = capitalize(form.value.fullName);
  form.value.location = capitalize(form.value.location);
  form.value.title = form.value.title.trim();
  form.value.targetRole = form.value.targetRole.trim();
  form.value.summary = form.value.summary.trim();

  // Filter out empty skills and certifications
  form.value.skills = form.value.skills.filter((s) => s.trim());
  form.value.certifications = form.value.certifications.filter((c) => c.trim());

  // Format work experience
  form.value.workExperience.forEach((job) => {
    job.title = capitalize(job.title);
    job.company = capitalize(job.company);
    job.location = capitalize(job.location);
  });

  // Format education
  form.value.education.forEach((edu) => {
    edu.degree = capitalize(edu.degree);
    edu.school = capitalize(edu.school);
    edu.location = capitalize(edu.location);
  });
};

const generateAutoSummary = () => {
  // Generate a basic summary if none provided
  if (form.value.summary.trim()) {
    return form.value.summary;
  }

  const experience = form.value.workExperience.filter((exp) => exp.title && exp.company);
  const skills = form.value.skills.filter((skill) => skill.trim());
  const yearsExp = experience.length > 0 ? `${experience.length}+ years of` : "";
  const role = form.value.targetRole || form.value.industry || "professional";

  return `${yearsExp} experience as a ${role} with expertise in ${skills
    .slice(0, 3)
    .join(", ")}. Proven track record of delivering results and driving growth.`.trim();
};

const handleSubmit = async () => {
  error.value = "";
  loading.value = true;

  try {
    formatFormData();

    const user = await waitForAuth();
    if (!user) {
      throw new Error("Please log in to generate your resume");
    }

    const idToken = await user.getIdToken();

    // Prepare the resume data
    const resumeData = {
      // Resume metadata
      title: form.value.title,
      summary: generateAutoSummary(),
      industry: form.value.industry,
      job_title: form.value.targetRole,

      // Profile data for AI processing
      profile: {
        name: form.value.fullName,
        email: form.value.email,
        phone: form.value.phone,
        linkedin: form.value.linkedin,
        location: form.value.location,
        summary: form.value.summary,

        // Work experience
        experience: form.value.workExperience
          .filter((exp) => exp.title && exp.company)
          .map((exp) => ({
            title: exp.title,
            company: exp.company,
            location: exp.location,
            startDate: exp.startDate,
            endDate: exp.endDate || null,
            description: exp.description,
          })),

        // Education
        education: form.value.education
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

        // Skills and certifications
        skills: form.value.skills,
        certifications: form.value.certifications.filter((cert) => cert.trim()),
        industry: form.value.industry,
      },

      // AI generation settings
      tone: "professional",
      template_id: "modern", // You can make this configurable
    };

    const response = await fetch(`${API_URL}/api/v1/resume`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${idToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(resumeData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.message || `Failed to generate resume (${response.status})`
      );
    }

    const data = await response.json();
    success("Resume generated successfully!");

    // Redirect to preview
    setTimeout(() => {
      window.location.href = `/preview?id=${data.id}`;
    }, 1000);
  } catch (err) {
    console.error("Error generating resume:", err);
    error.value = err.message || "Failed to generate resume. Please try again.";
    showError(error.value);
  } finally {
    loading.value = false;
  }
};

// Initialize form with default data
onMounted(() => {
  if (defaultForm) {
    form.value = { ...form.value, ...JSON.parse(JSON.stringify(defaultForm)) };
  }
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
</style>
