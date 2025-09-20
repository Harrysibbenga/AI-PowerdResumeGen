<template>
  <div class="relative">
    <!-- Autosave Status Bar -->
    <div class="sticky top-0 z-40 bg-white border-b border-gray-200 px-6 py-3 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h1 class="text-xl font-semibold text-gray-900">
            {{ isEditMode ? "Edit Resume" : "Create Resume" }}
          </h1>
          <AutosaveIndicator
            :status="autoSaveStatus"
            :last-saved-text="lastSavedText"
            :config="autoSaveConfig"
            :show-save-button="true"
            :show-settings="true"
            @save="handleManualSave"
            @retry="handleManualSave"
            @update-config="updateAutoSaveConfig"
          />
        </div>

        <!-- Form Actions -->
        <div class="flex items-center space-x-3">
          <!-- Debug buttons - only show in development or localhost -->
          <div 
            v-if="isDevelopment || isLocalhost" 
            class="flex items-center space-x-2 mr-4 px-3 py-1.5 bg-yellow-50 border border-yellow-200 rounded"
          >
            <span class="text-xs text-yellow-700 font-medium">Debug:</span>
            <button
              @click="handleDebugData"
              class="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200 transition-colors"
            >
              Log Data
            </button>
            <button
              @click="handleValidateData"
              class="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200 transition-colors"
            >
              Validate
            </button>
            <button
              @click="handleFixNulls"
              class="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200 transition-colors"
            >
              Fix Nulls
            </button>
          </div>

          <button
            v-if="hasUnsavedChanges"
            @click="handleManualSave"
            :disabled="isAutoSaving"
            class="text-sm px-3 py-1.5 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors disabled:opacity-50"
          >
            {{ isAutoSaving ? "Saving..." : "Save Draft" }}
          </button>

          <button
            @click="handlePreview"
            :disabled="!isFormValid"
            class="text-sm px-3 py-1.5 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Preview
          </button>
        </div>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-8 px-6 pb-8">
      <!-- Error Display -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <div class="flex items-start">
          <i class="pi pi-exclamation-triangle text-red-400 mr-3 mt-0.5 text-lg"></i>
          <div>
            <h3 class="text-sm font-medium text-red-800">Error</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Autosave Error -->
      <div
        v-if="autoSaveError"
        class="bg-amber-50 border border-amber-200 rounded-lg p-4"
      >
        <div class="flex items-start">
          <i class="pi pi-exclamation-triangle text-amber-400 mr-3 mt-0.5 text-lg"></i>
          <div class="flex-1">
            <h3 class="text-sm font-medium text-amber-800">Autosave Issue</h3>
            <p class="text-sm text-amber-700 mt-1">{{ autoSaveError }}</p>
          </div>
          <button
            @click="handleManualSave"
            class="text-sm text-amber-800 underline hover:no-underline"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8">
        <i class="pi pi-spin pi-spinner text-4xl text-primary-600 mb-4"></i>
        <p class="text-primary-600 font-medium">
          {{ isEditMode ? "Updating your resume..." : "Generating your resume..." }}
        </p>
        <p class="text-gray-500 text-sm mt-2">This may take a few moments</p>
      </div>

      <!-- Form Sections -->
      <div v-else-if="resumeData" class="space-y-8">
        <!-- Resume Details Section -->
        <FormSection
          title="Resume Details"
          description="Basic information about your resume"
        >
          <ResumeDetailsSection v-model="resumeData" @change="handleFormChange" />
        </FormSection>

        <!-- Personal Information -->
        <FormSection title="Personal Information" description="Your contact details">
          <PersonalInfoSection v-model="resumeData" @change="handleFormChange" />
        </FormSection>

        <!-- Industry Selection -->
        <FormSection title="Industry & Target" description="Define your career focus">
          <IndustrySelector
            v-model="resumeData.industry"
            @industryChanged="handleIndustryChange"
            @change="handleFormChange"
          />
        </FormSection>

        <!-- Professional Summary Section -->
        <FormSection
          title="Professional Summary"
          description="Brief overview of your experience"
        >
          <ProfessionalSummarySection v-model="resumeData" @change="handleFormChange" />
        </FormSection>

        <!-- AI Generation Settings -->
        <FormSection
          title="AI Settings"
          description="Customize how AI enhances your resume"
        >
          <AIGenerationSettings v-model="resumeData" @change="handleFormChange" />
        </FormSection>

        <!-- Include Sections -->
        <FormSection
          title="Resume Sections"
          description="Choose what to include in your resume"
        >
          <IncludeSections v-model="resumeData" @change="handleFormChange" />
        </FormSection>

        <!-- Skills -->
        <FormSection
          title="Skills"
          description="Your technical and professional abilities"
        >
          <SkillsInput
            v-model="resumeData.skills"
            :industry="safeResumeData.industry"
            @change="handleFormChange"
          />
        </FormSection>

        <!-- Work Experience -->
        <FormSection title="Work Experience" description="Your professional background">
          <WorkExperienceInput
            v-model="resumeData.workExperience"
            @change="handleFormChange"
          />
        </FormSection>

        <!-- Education -->
        <FormSection title="Education" description="Your academic background">
          <EducationInput v-model="resumeData.education" @change="handleFormChange" />
        </FormSection>

        <!-- Certifications -->
        <FormSection
          v-if="safeResumeData.includeCertifications"
          title="Certifications"
          description="Professional certifications and credentials"
        >
          <CertificationsInput
            v-model="resumeData.certifications"
            :industry="safeResumeData.industry"
            @change="handleFormChange"
          />
        </FormSection>

        <!-- Projects -->
        <FormSection
          v-if="safeResumeData.includeProjects"
          title="Projects"
          description="Notable projects and achievements"
        >
          <ProjectsInput v-model="resumeData.projects" @change="handleFormChange" />
        </FormSection>

        <!-- Languages -->
        <FormSection
          v-if="safeResumeData.includeLanguages"
          title="Languages"
          description="Languages you speak"
        >
          <Languages v-model="resumeData.languages" @change="handleFormChange" />
        </FormSection>

        <!-- Submit Section -->
        <div class="bg-gray-50 rounded-lg p-6">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-medium text-gray-900">Ready to generate?</h3>
              <p class="text-sm text-gray-600 mt-1">
                {{
                  isEditMode
                    ? "Update your resume with the latest changes"
                    : "Create your professional resume"
                }}
              </p>
            </div>

            <div class="flex items-center space-x-3">
              <button
                type="button"
                @click="handleSaveAsDraft"
                :disabled="!resumeData || isAutoSaving"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Save as Draft
              </button>

              <SubmitButton
                :loading="loading"
                :disabled="!isFormValid"
                :is-edit-mode="isEditMode"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Fallback for null resumeData -->
      <div v-else class="text-center py-8">
        <i class="pi pi-spin pi-spinner text-4xl text-gray-400 mb-4"></i>
        <p class="text-gray-600 font-medium">Initializing form...</p>
        <p class="text-gray-500 text-sm mt-2">Loading resume data structure</p>
      </div>
    </form>

    <!-- Confirmation Dialog for Unsaved Changes -->
    <ConfirmDialog
      v-if="showUnsavedDialog"
      title="Unsaved Changes"
      message="You have unsaved changes. Do you want to save them before leaving?"
      confirm-text="Save & Continue"
      cancel-text="Discard Changes"
      @confirm="handleSaveAndContinue"
      @cancel="handleDiscardAndContinue"
      @close="showUnsavedDialog = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";
import { useResumeData } from "@/composables/useResumeData";
import { resumeClient } from "@/lib/resume/ResumeClient";

// Component imports
import AutosaveIndicator from "./AutosaveIndicator.vue";
import FormSection from "./FormSection.vue";
import ConfirmDialog from "./ConfirmDialog.vue";
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

// Props
const props = defineProps({
  initialData: {
    type: Object,
    default: null,
  },
});

// Composables
const { waitForAuth } = useFirebase();
const { success, error: showError, info } = useToast();
const {
  resumeData,
  isEditMode,
  currentResumeId,
  initializeFormData,
  toApiPayload,
  validateFormData,
  validateDataIntegrity,
  fixNullValues,
  clearStorage,
  // Autosave functionality
  isAutoSaving,
  lastSaved,
  isDirty,
  autoSaveError,
  hasUnsavedChanges,
  autoSaveStatus,
  lastSavedText,
  forceSave,
  updateAutoSaveConfig: updateConfig,
  setAutoSaveEnabled,
} = useResumeData();

// Local state
const loading = ref(false);
const error = ref("");
const showUnsavedDialog = ref(false);
const pendingNavigation = ref(null);
const autoSaveConfig = ref({
  enabled: true,
  interval: 3000,
  showNotifications: false,
  storageKey: "resumeFormData",
  maxRetries: 3,
  retryDelay: 1000,
});

// Check if we're in browser environment
const isBrowser = typeof window !== "undefined";

// Computed properties
const isFormValid = computed(() => {
  if (!resumeData.value) return false;
  const validation = validateFormData(resumeData.value);
  return validation.isValid;
});

const isDevelopment = computed(() => process.env.NODE_ENV === 'development');
const isLocalhost = computed(() => isBrowser && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'));

// Safe access to resume data with defaults
const safeResumeData = computed(() => {
  const result = resumeData.value || {
    includeProjects: false,
    includeCertifications: false,
    includeLanguages: false,
    industry: '',
    skills: [],
    workExperience: [],
    education: [],
    certifications: [],
    projects: [],
    languages: []
  };
  
  // Debug logging for section visibility
  if (resumeData.value) {
    console.log('safeResumeData computed - actual data:', {
      includeProjects: result.includeProjects,
      includeCertifications: result.includeCertifications,
      includeLanguages: result.includeLanguages,
      projectsLength: result.projects?.length,
      languagesLength: result.languages?.length,
      certificationsLength: result.certifications?.length
    });
  }
  
  return result;
});

// Methods
const handleFormChange = () => {
  // This will be called by child components when they change
  // The autosave watcher will handle the actual saving
};

const handleIndustryChange = () => {
  if (resumeData.value?.industry && !resumeData.value?.targetJobTitle) {
    // Could implement industry-based suggestions here
  }
};

const handleManualSave = async () => {
  try {
    const result = await forceSave();
    if (result.success) {
      success("Draft saved successfully");
    } else {
      showError("Failed to save draft: " + result.error);
    }
  } catch (error) {
    console.error("Manual save error:", error);
    showError("Failed to save draft");
  }
};

const handleSaveAsDraft = async () => {
  await handleManualSave();
};

const handlePreview = () => {
  if (hasUnsavedChanges.value) {
    showUnsavedDialog.value = true;
    pendingNavigation.value = "preview";
  } else {
    navigateToPreview();
  }
};

const navigateToPreview = () => {
  if (isBrowser && resumeData.value?.id) {
    window.location.href = `/preview?id=${resumeData.value.id}`;
  }
};

const generateAutoSummary = (data) => {
  if (!data.summary?.trim()) {
    const experience = data.workExperience?.[0];
    const yearsExp = calculateYearsOfExperience(data.workExperience);

    return `${
      data.targetJobTitle || "Professional"
    } with ${yearsExp} years of experience${
      experience?.company ? ` at ${experience.company}` : ""
    }. Skilled in ${data.skills?.slice(0, 3).join(", ") || "various technologies"}.`;
  }
  return data.summary;
};

const calculateYearsOfExperience = (workExp) => {
  if (!Array.isArray(workExp) || workExp.length === 0) return "0+";

  const currentDate = new Date();
  let totalMonths = 0;

  workExp.forEach((exp) => {
    if (exp.startDate) {
      const startDate = new Date(exp.startDate);
      const endDate = exp.current || !exp.endDate ? currentDate : new Date(exp.endDate);

      if (!isNaN(startDate.getTime()) && !isNaN(endDate.getTime())) {
        totalMonths +=
          (endDate.getFullYear() - startDate.getFullYear()) * 12 +
          (endDate.getMonth() - startDate.getMonth());
      }
    }
  });

  const years = Math.floor(totalMonths / 12);
  return years > 0 ? `${years}+` : "1+";
};

const handleSubmit = async () => {
  error.value = "";
  loading.value = true;

  try {
    // Validate form data
    const validation = validateFormData(resumeData.value);
    if (!validation.isValid) {
      throw new Error(
        `Please fix the following errors:\n${validation.errors.join("\n")}`
      );
    }

    // Wait for authentication
    const user = await waitForAuth();
    if (!user) {
      throw new Error("Please log in to generate your resume");
    }

    // Save any pending changes first
    if (hasUnsavedChanges.value) {
      await forceSave();
    }

    // Generate auto summary if needed
    if (!resumeData.value.summary?.trim()) {
      resumeData.value.summary = generateAutoSummary(resumeData.value);
    }

    // Convert to API payload format
    const payload = toApiPayload(resumeData.value);

    let response;
    if (isEditMode.value && currentResumeId.value) {
      // Update existing resume
      response = await resumeClient.updateResume(currentResumeId.value, payload);
      success("Resume updated successfully!");
    } else {
      // Create new resume
      response = await resumeClient.generateResume(payload);
      success("Resume generated successfully!");
    }

    // Clear localStorage after successful submission
    clearStorage();

    // Navigate to preview
    setTimeout(() => {
      if (isBrowser) {
        const resumeId = response.id || response.data?.id || currentResumeId.value;
        window.location.href = `/preview?id=${resumeId}`;
      }
    }, 1000);
  } catch (err) {
    console.error("Resume submission error:", err);

    let errorMessage = "Failed to process resume. Please try again.";

    // Handle different error types
    if (err.response?.status === 422) {
      console.error("Validation error details:", err.response.data);

      if (err.response.data.detail) {
        if (Array.isArray(err.response.data.detail)) {
          const validationErrors = err.response.data.detail
            .map((error) => `${error.loc.join(".")}: ${error.msg}`)
            .join(", ");
          errorMessage = `Validation errors: ${validationErrors}`;
        } else {
          errorMessage = err.response.data.detail;
        }
      }
    } else if (err.message) {
      errorMessage = err.message;
    }

    error.value = errorMessage;
    showError(errorMessage);
  } finally {
    loading.value = false;
  }
};

const handleSaveAndContinue = async () => {
  await handleManualSave();
  showUnsavedDialog.value = false;

  if (pendingNavigation.value === "preview") {
    navigateToPreview();
  }

  pendingNavigation.value = null;
};

const handleDiscardAndContinue = () => {
  showUnsavedDialog.value = false;

  if (pendingNavigation.value === "preview") {
    navigateToPreview();
  }

  pendingNavigation.value = null;
};

const updateAutoSaveConfig = (newConfig) => {
  autoSaveConfig.value = { ...autoSaveConfig.value, ...newConfig };
  updateConfig(newConfig);
};

// Debug handlers
const handleDebugData = () => {
  console.log('=== MANUAL DEBUG DATA DUMP ===');
  console.log('Current resumeData:', JSON.stringify(resumeData.value, null, 2));
  console.log('Form validation:', validateFormData(resumeData.value));
  console.log('safeResumeData flags:', {
    includeProjects: safeResumeData.value.includeProjects,
    includeCertifications: safeResumeData.value.includeCertifications,
    includeLanguages: safeResumeData.value.includeLanguages,
  });
  console.log('Data arrays:', {
    projects: resumeData.value?.projects?.length || 0,
    certifications: resumeData.value?.certifications?.length || 0,
    languages: resumeData.value?.languages?.length || 0,
  });
  console.log('Environment details:');
  console.log('- NODE_ENV:', process.env.NODE_ENV);
  console.log('- hostname:', window.location.hostname);
  console.log('- href:', window.location.href);
  console.log('- localStorage keys:', Object.keys(localStorage));
  console.log('=== END MANUAL DEBUG ===');
  info('Debug data logged to console');
};

const handleValidateData = () => {
  console.log('=== MANUAL VALIDATION ===');
  validateDataIntegrity(resumeData.value, 'manualValidation');
  console.log('=== END MANUAL VALIDATION ===');
  info('Validation complete - check console');
};

const handleFixNulls = () => {
  console.log('=== MANUAL NULL FIX ===');
  fixNullValues();
  console.log('=== END MANUAL NULL FIX ===');
  success('Null values fixed');
};

// Lifecycle
onMounted(async () => {
  console.log('ResumeForm onMounted - starting initialization...');
  
  try {
    // Initialize form data
    const initialData = props.initialData || null;
    console.log('ResumeForm: calling initializeFormData with:', { hasInitialData: !!initialData });
    
    const result = initializeFormData(initialData);
    
    console.log('ResumeForm: initialization completed:', {
      hasResult: !!result,
      hasResumeData: !!resumeData.value,
      titleValue: resumeData.value?.title,
      includeFlags: {
        projects: resumeData.value?.includeProjects,
        certifications: resumeData.value?.includeCertifications,
        languages: resumeData.value?.includeLanguages
      }
    });
    
    // Small delay to ensure Vue reactivity has processed
    await nextTick();
    console.log('ResumeForm: after nextTick, resumeData is:', !!resumeData.value);
    
  } catch (error) {
    console.error('ResumeForm: initialization error:', error);
    showError('Failed to initialize form data');
  }

  console.log("Form initialized:", {
    isEditMode: isEditMode.value,
    resumeId: currentResumeId.value,
    hasData: !!resumeData.value,
    autoSaveEnabled: autoSaveConfig.value.enabled,
  });

  // Log the complete resumeData structure for debugging
  console.log("=== RESUME DATA DEBUG ===");
  console.log("ResumeData structure:", JSON.stringify(resumeData.value, null, 2));
  console.log("Include sections:");
  console.log("- includeProjects:", resumeData.value?.includeProjects);
  console.log("- includeCertifications:", resumeData.value?.includeCertifications);
  console.log("- includeLanguages:", resumeData.value?.includeLanguages);
  console.log("Null/undefined values:");
  Object.entries(resumeData.value || {}).forEach(([key, value]) => {
    if (value === null || value === undefined || value === '') {
      console.log(`- ${key}: ${value}`);
    }
  });
  console.log("=== END DEBUG ===");

  // Set up autosave config
  updateConfig(autoSaveConfig.value);

  // Watch for resumeData changes for debugging
  watch(resumeData, (newData, oldData) => {
    console.log("=== RESUME FORM DATA WATCHER ===");
    console.log("Form data change detected:");
    console.log("- includeProjects:", oldData?.includeProjects, "->", newData?.includeProjects);
    console.log("- includeCertifications:", oldData?.includeCertifications, "->", newData?.includeCertifications);
    console.log("- includeLanguages:", oldData?.includeLanguages, "->", newData?.includeLanguages);
    
    // Check for null values being introduced
    if (newData) {
      const newNullKeys = Object.entries(newData).filter(([key, value]) => 
        value === null || value === undefined || value === ''
      ).map(([key]) => key);
      
      const oldNullKeys = oldData ? Object.entries(oldData).filter(([key, value]) => 
        value === null || value === undefined || value === ''
      ).map(([key]) => key) : [];
      
      const newlyNull = newNullKeys.filter(key => !oldNullKeys.includes(key));
      const nowFilled = oldNullKeys.filter(key => !newNullKeys.includes(key));
      
      if (newlyNull.length > 0) {
        console.log("Newly null/empty fields:", newlyNull);
      }
      if (nowFilled.length > 0) {
        console.log("Newly filled fields:", nowFilled);
      }
    }
    console.log("=== END FORM WATCHER ===");
  }, { deep: true });
});

onUnmounted(() => {
  // Cleanup is handled by the composable
});

// Expose methods for parent components
defineExpose({
  resumeData,
  validateFormData: () => validateFormData(resumeData.value),
  submitForm: handleSubmit,
  saveAsDraft: handleManualSave,
  resetForm: () => {
    resumeData.value = initializeFormData();
    clearStorage();
  },
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
