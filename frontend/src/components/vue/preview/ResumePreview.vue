<template>
  <div class="max-w-4xl mx-auto p-6">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"
      ></div>
      <p class="text-gray-600">Loading resume...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <div class="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
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
    <div v-else class="bg-white shadow-lg rounded-lg p-8">
      <!-- Header -->
      <header class="text-center mb-8 border-b border-gray-200 pb-6">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">
          {{ resumeData.name || "Resume Preview" }}
        </h1>
        <p v-if="resumeData.email || resumeData.phone" class="text-gray-600 mb-2">
          <span v-if="resumeData.email">{{ resumeData.email }}</span>
          <span v-if="resumeData.email && resumeData.phone"> | </span>
          <span v-if="resumeData.phone">{{ resumeData.phone }}</span>
        </p>
        <p v-if="resumeData.location" class="text-gray-600">{{ resumeData.location }}</p>
      </header>

      <!-- Professional Summary -->
      <section v-if="resumeData.summary" class="mb-8">
        <h2
          class="text-2xl font-semibold text-gray-900 mb-3 border-l-4 border-blue-600 pl-3"
        >
          Professional Summary
        </h2>
        <p class="text-gray-700 leading-relaxed">{{ resumeData.summary }}</p>
      </section>

      <!-- Experience -->
      <section v-if="resumeData.experience?.length" class="mb-8">
        <h2
          class="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-3"
        >
          Professional Experience
        </h2>
        <div class="space-y-6">
          <div
            v-for="(exp, index) in resumeData.experience"
            :key="`exp-${index}`"
            class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
          >
            <div class="flex flex-col md:flex-row md:justify-between md:items-start mb-3">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">{{ exp.title }}</h3>
                <p class="text-blue-600 font-medium">{{ exp.company }}</p>
              </div>
              <div class="text-sm text-gray-500 mt-1 md:mt-0">
                <p>{{ formatDateRange(exp.startDate, exp.endDate) }}</p>
                <p v-if="exp.location" class="text-gray-400">{{ exp.location }}</p>
              </div>
            </div>

            <!-- Job Description -->
            <div v-if="exp.description?.length" class="mt-3">
              <ul class="space-y-1">
                <li
                  v-for="(desc, descIndex) in exp.description"
                  :key="`desc-${index}-${descIndex}`"
                  class="flex items-start"
                >
                  <span class="text-blue-600 mr-2 mt-1.5 flex-shrink-0">•</span>
                  <span class="text-gray-700">{{ desc }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- Education -->
      <section v-if="resumeData.education?.length" class="mb-8">
        <h2
          class="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-3"
        >
          Education
        </h2>
        <div class="space-y-4">
          <div
            v-for="(edu, index) in resumeData.education"
            :key="`edu-${index}`"
            class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
          >
            <div class="flex flex-col md:flex-row md:justify-between md:items-start">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">{{ edu.degree }}</h3>
                <p class="text-blue-600 font-medium">{{ edu.institution }}</p>
                <p v-if="edu.gpa" class="text-sm text-gray-600">GPA: {{ edu.gpa }}</p>
              </div>
              <div class="text-sm text-gray-500 mt-1 md:mt-0 text-right">
                <p>{{ formatDateRange(edu.startYear, edu.endYear) }}</p>
                <p v-if="edu.location" class="text-gray-400">{{ edu.location }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Skills -->
      <section v-if="hasSkills" class="mb-8">
        <h2
          class="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-3"
        >
          Skills
        </h2>
        <div class="space-y-4">
          <div
            v-for="(skillList, category) in resumeData.skills"
            :key="category"
            class="border border-gray-200 rounded-lg p-4"
          >
            <h3 class="font-semibold text-gray-900 mb-3 capitalize">{{ category }}</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(skill, skillIndex) in skillList"
                :key="`skill-${category}-${skillIndex}`"
                class="inline-block px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-full hover:bg-blue-200 transition-colors"
              >
                {{ skill }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Projects (if available) -->
      <section v-if="resumeData.projects?.length" class="mb-8">
        <h2
          class="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-3"
        >
          Projects
        </h2>
        <div class="space-y-4">
          <div
            v-for="(project, index) in resumeData.projects"
            :key="`project-${index}`"
            class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
          >
            <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ project.name }}</h3>
            <p v-if="project.description" class="text-gray-700 mb-2">
              {{ project.description }}
            </p>
            <div v-if="project.technologies?.length" class="flex flex-wrap gap-1">
              <span
                v-for="tech in project.technologies"
                :key="tech"
                class="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
              >
                {{ tech }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Action Buttons -->
      <div class="flex justify-center gap-4 mt-8 pt-6 border-t border-gray-200">
        <button
          @click="downloadPDF"
          :disabled="downloading"
          class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-2 rounded-lg transition-colors flex items-center gap-2"
        >
          <span v-if="downloading">Generating...</span>
          <span v-else>Download PDF</span>
        </button>
        <button
          @click="editResume"
          class="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg transition-colors"
        >
          Edit Resume
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";

const props = defineProps({
  resumeId: {
    type: String,
    required: false,
  },
});

const resumeData = ref({
  name: "",
  email: "",
  phone: "",
  location: "",
  summary: "",
  experience: [],
  education: [],
  skills: {},
  projects: [],
});

const loading = ref(true);
const error = ref(null);
const downloading = ref(false);

const { waitForAuth, getAuth } = useFirebase();
const { success, error: showError } = useToast();

const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

// Computed properties
const hasSkills = computed(() => {
  return resumeData.value.skills && Object.keys(resumeData.value.skills).length > 0;
});

// Helper methods
const formatDateRange = (startDate, endDate) => {
  if (!startDate) return "N/A";
  const start = formatDate(startDate);
  const end = endDate ? formatDate(endDate) : "Present";
  return `${start} - ${end}`;
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
    });
  } catch {
    return dateString; // Return as-is if parsing fails
  }
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

    // Map the response data to our component structure
    resumeData.value = {
      name: data.profile_data?.name || data.ai_content?.name || "Resume Preview",
      email: data.profile_data?.email || "",
      phone: data.profile_data?.phone || "",
      location: data.profile_data?.location || "",
      summary: data.ai_content?.summary || data.profile_data?.summary || "",
      experience: data.ai_content?.experience || [],
      education: data.ai_content?.education || [],
      skills: data.ai_content?.skills || {},
      projects: data.ai_content?.projects || [],
    };
  } catch (err) {
    console.error("Error loading resume:", err);
    error.value = err.message || "Failed to load resume";
    showError(err.message || "Failed to load resume");
  } finally {
    loading.value = false;
  }
};

const downloadPDF = async () => {
  try {
    downloading.value = true;
    const resumeId = getResumeId();
    const user = await waitForAuth();

    if (!user) {
      showError("Please log in to download your resume");
      return;
    }

    const token = await user.getIdToken();
    const response = await fetch(`${API_URL}/api/v1/resume/${resumeId}/download`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to generate PDF");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${resumeData.value.name || "resume"}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    success("Resume downloaded successfully!");
  } catch (err) {
    console.error("Error downloading PDF:", err);
    showError("Failed to download resume");
  } finally {
    downloading.value = false;
  }
};

const editResume = () => {
  const resumeId = getResumeId();
  window.location.href = `/builder?id=${resumeId}`;
};

// Initialize
onMounted(() => {
  loadResume();
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
