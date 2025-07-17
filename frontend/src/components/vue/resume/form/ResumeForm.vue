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
      <ProjectsInput v-if="form.includeProjects" v-model="form.projects" />

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
import { formatFormData, generateAutoSummary } from "@/utils/resumeHelpers";
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

const handleSubmit = async () => {
  error.value = "";
  loading.value = true;

  try {
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

onMounted(() => {
  form.value = { ...form.value, ...JSON.parse(JSON.stringify(defaultForm)) };
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
