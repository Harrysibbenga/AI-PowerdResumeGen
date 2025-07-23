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
      <!-- Resume Details Section -->
      <ResumeDetailsSection v-model="form" />

      <!-- Personal Information -->
      <PersonalInfoSection v-model="form" />

      <!-- Industry Selection -->
      <IndustrySelector v-model="form.industry" @industryChanged="handleIndustryChange" />

      <!-- Professional Summary Section -->
      <ProfessionalSummarySection v-model="form" />

      <!-- AI Generation Settings -->
      <AIGenerationSettings v-model="form" />

      <!-- Include Sections -->
      <IncludeSections v-model="form" />

      <!-- Skills -->
      <SkillsInput v-model="form.skills" :industry="form.industry" />

      <!-- Certifications -->
      <CertificationsInput
        v-if="form.includeCertifications"
        v-model="form.certifications"
        :industry="form.industry"
      />

      <!-- Work Experience -->
      <WorkExperienceInput v-model="form.workExperience" />

      <!-- Education -->
      <EducationInput v-model="form.education" />

      <!-- Projects -->
      <ProjectsInput v-if="form.includeProjects" v-model="form" />

      <!-- Languages -->
      <Languages v-if="form.includeLanguages" v-model="form" />

      <!-- Submit Button -->
      <SubmitButton :loading="loading" :disabled="loading || !isFormValid" />
    </div>
  </form>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";
import { resumeClient } from "@/lib/resume/ResumeClient";

import ResumeDetailsSection from "./ResumeDetailsSection.vue";
import ProfessionalSummarySection from "./ProfessionalSummarySection.vue";
import PersonalInfoSection from "./PersonalInfoSection.vue";
import IndustrySelector from "./IndustrySelector.vue";
import AIGenerationSettings from "./AIGenerationSettings.vue";
import SkillsInput from "./SkillsInput.vue";
import CertificationsInput from "./CertificationsInput.vue";
import IncludeSections from "./IncludeSections.vue";
import WorkExperienceInput from "./WorkExperienceInput.vue";
import EducationInput from "./EducationInput.vue";
import ProjectsInput from "./ProjectsInput.vue";
import Languages from "./Languages.vue";
import SubmitButton from "./SubmitButton.vue";

import { defaultForm } from "@/utils/defaultForm.js";
import { capitalize } from "@/utils/formatters.js";
import { useResumeForm } from "@/composables/useResumeForm";
import {
  formatFormData,
  generateAutoSummary,
  migrateLanguagesFormat,
  validateProject,
  validateLanguage,
} from "@/utils/resumeHelpers";
import { buildResumePayload } from "@/utils/buildResumePayload";

// Base state
const loading = ref(false);
const error = ref("");
const form = ref(JSON.parse(JSON.stringify(defaultForm)));

const { waitForAuth } = useFirebase();
const { success, error: showError } = useToast();

// Validation
const isFormValid = computed(() => {
  return (
    form.value?.title?.trim?.() &&
    form.value?.targetJobTitle?.trim?.() &&
    form.value?.fullName?.trim?.() &&
    form.value?.email?.trim?.() &&
    form.value?.industry?.trim?.()
  );
});

const handleIndustryChange = () => {
  if (form.value.industry && !form.value.targetJobTitle) {
    // Optional: suggest job title
  }
};

const validateFormData = () => {
  const errors = [];

  // Validate projects if included
  if (form.value.includeProjects && form.value.projects) {
    form.value.projects.forEach((project, index) => {
      const validation = validateProject(project);
      if (!validation.isValid) {
        errors.push(`Project ${index + 1}: ${validation.errors.join(", ")}`);
      }
    });
  }

  // Validate languages if included
  if (form.value.includeLanguages && form.value.languages) {
    form.value.languages.forEach((language, index) => {
      const validation = validateLanguage(language);
      if (!validation.isValid) {
        errors.push(`Language ${index + 1}: ${validation.errors.join(", ")}`);
      }
    });
  }

  return errors;
};

const hasExistingData = (formData) => {
  // Check if any key personal fields have been filled with non-default values
  const hasPersonalInfo =
    formData.fullName &&
    formData.fullName !== "John Doe" &&
    formData.email &&
    formData.email !== "john.doe@example.com";

  // Check if work experience has been customized
  const hasCustomWork =
    formData.workExperience &&
    formData.workExperience.length > 0 &&
    formData.workExperience[0].company !== "CyberSafe Ltd";

  // Check if education has been customized
  const hasCustomEducation =
    formData.education &&
    formData.education.length > 0 &&
    formData.education[0].school !== "Tech University";

  return hasPersonalInfo || hasCustomWork || hasCustomEducation;
};

// Create empty form structure
const createEmptyForm = () => {
  return {
    // Personal Information
    fullName: "",
    email: "",
    phone: "",
    linkedin: "",
    location: "",

    // Resume Details
    title: "",
    targetJobTitle: "",
    targetJobRole: "",
    targetCompany: "",
    industry: "",

    // Professional Summary
    summary: "",

    // Skills
    skills: [],

    // Work Experience
    workExperience: [
      {
        title: "",
        company: "",
        location: "",
        startDate: "",
        endDate: "",
        description: "",
        highlights: [""],
      },
    ],

    // Education
    education: [
      {
        degree: "",
        school: "",
        location: "",
        graduationDate: "",
        description: "",
        gpa: "",
      },
    ],

    // Section toggles
    includeProjects: false,
    includeCertifications: false,
    includeLanguages: false,

    // Projects
    projects: [],

    // Certifications
    certifications: [],

    // Languages
    languages: [],

    // AI Settings
    useAI: true,
    aiTone: "professional",
    aiLength: "standard",
  };
};

const handleSubmit = async () => {
  error.value = "";
  loading.value = true;

  try {
    // Validate form data before processing
    const validationErrors = validateFormData();
    if (validationErrors.length > 0) {
      throw new Error(`Please fix the following errors:\n${validationErrors.join("\n")}`);
    }

    formatFormData(form.value);

    const user = await waitForAuth();
    if (!user) throw new Error("Please log in to generate your resume");

    if (!form.value.summary.trim()) {
      form.value.summary = generateAutoSummary(form.value);
    }

    const payload = buildResumePayload(form.value);
    const response = await resumeClient.generateResume(payload);

    success("Resume generated successfully!");
    setTimeout(() => {
      window.location.href = `/preview?id=${response.id}`;
    }, 1000);
  } catch (err) {
    console.error("Resume generation error:", err);
    error.value = err.message || "Failed to generate resume. Please try again.";
    showError(error.value);
  } finally {
    loading.value = false;
  }
};

// Migration and initialization logic
const migrateFormData = (formData) => {
  // Migrate languages from old string format to new object format
  if (formData.languages && Array.isArray(formData.languages)) {
    formData.languages = migrateLanguagesFormat(formData.languages);
  }

  // Ensure projects have the correct structure
  if (formData.projects && Array.isArray(formData.projects)) {
    formData.projects = formData.projects.map((project) => {
      // Ensure all required fields exist
      return {
        title: project.title || "",
        description: project.description || "",
        technologies: project.technologies || [],
        url: project.url || "",
        startDate: project.startDate || "",
        endDate: project.endDate || "",
        highlights: project.highlights || [""],
        ...project, // Keep any additional fields
      };
    });
  }

  return formData;
};

onMounted(() => {
  // Check if there's existing data from localStorage, props, or API
  let existingData = null;

  // Try to load from localStorage
  try {
    const saved = localStorage.getItem("resumeFormData");
    if (saved) {
      existingData = JSON.parse(saved);
    }
  } catch (e) {
    console.warn("Could not load saved form data:", e);
  }

  // You can also check for data from props or route params here
  // existingData = props.initialData || existingData;

  let initialForm;

  if (existingData && hasExistingData(existingData)) {
    // Use existing data and migrate it
    console.log("Loading existing form data");
    initialForm = migrateFormData(existingData);
  } else {
    // Determine whether to use test data or empty form
    const useTestData =
      process.env.NODE_ENV === "development" ||
      new URLSearchParams(window.location.search).has("testdata");

    if (useTestData) {
      console.log("Using test data for development");
      initialForm = migrateFormData(JSON.parse(JSON.stringify(defaultForm)));
    } else {
      console.log("Creating new empty form");
      initialForm = createEmptyForm();
    }
  }

  // Set the form data
  form.value = initialForm;

  console.log("Form initialized:", {
    hasData: hasExistingData(form.value),
    form: form.value,
  });
});

// Optional: Add a method to handle loading saved data
const loadSavedData = (savedData) => {
  const migratedData = migrateFormData(savedData);
  form.value = { ...form.value, ...migratedData };
};

// Export for potential use by parent components
defineExpose({
  loadSavedData,
  validateFormData,
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
