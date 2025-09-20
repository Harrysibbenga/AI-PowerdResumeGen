<template>
  <div class="bg-white rounded-lg shadow p-6 mb-8">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">Your Resumes</h2>
      <a
        href="/builder"
        class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors"
        @click="clearFormData"
      >
        Create New Resume
      </a>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Loading State -->
      <div
        v-if="loading || !authInitialized"
        class="col-span-full flex justify-center items-center py-12"
      >
        <i class="pi pi-spin pi-spinner text-2xl text-primary-600 mr-3"></i>
        <span class="text-gray-600">
          {{ !authInitialized ? "Initializing..." : "Loading resumes..." }}
        </span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="col-span-full">
        <div class="border border-red-200 rounded-lg p-6 bg-red-50">
          <div class="flex items-start">
            <i class="pi pi-exclamation-triangle text-red-500 mr-3 mt-1"></i>
            <div class="flex-1">
              <p class="text-red-600 font-medium">Failed to load resumes</p>
              <p class="text-red-600 text-sm mt-1">{{ error }}</p>
            </div>
          </div>
          <button
            @click="fetchResumes"
            class="mt-4 w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg transition-colors"
          >
            <i class="pi pi-refresh mr-2"></i>
            Try Again
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <NoResumesFound v-else-if="resumes.length === 0" />

      <!-- Resume Grid -->
      <ResumeCard
        v-else
        v-for="resume in normalizedResumes"
        :key="resume.id"
        :resume="resume"
        @delete="handleDeleteResume"
        @view="viewResume"
        @edit="editResume"
        @duplicate="duplicateResume"
        @export="exportResume"
        @share="shareResume"
        @regenerate="regenerateContent"
      />
    </div>

    <!-- Pagination (if needed) -->
    <div
      v-if="pagination && pagination.total > pagination.perPage"
      class="mt-8 flex justify-center"
    >
      <nav class="flex items-center space-x-2">
        <button
          @click="changePage(pagination.currentPage - 1)"
          :disabled="pagination.currentPage <= 1"
          class="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <i class="pi pi-chevron-left"></i>
        </button>

        <span class="px-3 py-2 text-sm text-gray-700">
          Page {{ pagination.currentPage }} of {{ pagination.totalPages }}
        </span>

        <button
          @click="changePage(pagination.currentPage + 1)"
          :disabled="pagination.currentPage >= pagination.totalPages"
          class="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <i class="pi pi-chevron-right"></i>
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";
import { useResumeData } from "@/composables/useResumeData";
import { resumeClient } from "@/lib/resume/ResumeClient";
import NoResumesFound from "./NoResumesFound.vue";
import ResumeCard from "./ResumeCard.vue";

// Reactive state
const resumes = ref([]);
const loading = ref(false);
const error = ref(null);
const pagination = ref(null);

// Check if we're in browser environment
const isBrowser = typeof window !== "undefined";

// Composables
const { user, isAuthenticated, authInitialized, initAuth, waitForAuth } = useFirebase();
const { success, error: showError } = useToast();
const { normalizeApiResponse, clearStorage, saveToStorage } = useResumeData();

// Computed properties
const normalizedResumes = computed(() => {
  return resumes.value.map((resume) => normalizeApiResponse(resume));
});

// Methods
const fetchResumes = async (page = 1, perPage = 12) => {
  if (!isBrowser) return;

  try {
    loading.value = true;
    error.value = null;

    const currentUser = await waitForAuth();
    if (!currentUser) {
      showError("Please log in to view your resumes");
      setTimeout(() => (window.location.href = "/login"), 1500);
      return;
    }

    const response = await resumeClient.listResumes({
      page,
      perPage,
      sortBy: "updated_at",
      sortOrder: "desc",
    });

    // Handle different response structures
    if (Array.isArray(response)) {
      resumes.value = response;
      pagination.value = null;
    } else if (response.data || response.resumes) {
      resumes.value = response.data || response.resumes;
      pagination.value = response.pagination || response.meta || null;
    } else {
      resumes.value = [];
    }

    // Calculate pagination if not provided by API
    if (!pagination.value && resumes.value.length > 0) {
      pagination.value = {
        currentPage: page,
        perPage,
        total: resumes.value.length,
        totalPages: Math.ceil(resumes.value.length / perPage),
      };
    }
  } catch (err) {
    console.error("Error fetching resumes:", err);
    error.value = err.message || "Failed to load resumes";

    if (err.message.includes("401") || err.message.includes("unauthorized")) {
      showError("Session expired. Please log in again.");
      setTimeout(() => (window.location.href = "/login"), 1500);
    } else {
      showError("Failed to load resumes");
    }
  } finally {
    loading.value = false;
  }
};

const clearFormData = () => {
  if (!isBrowser) return;
  clearStorage(["resumeFormData", "currentResumeId", "editMode"]);
};

const viewResume = (resume) => {
  if (!isBrowser) return;
  window.location.href = `/preview?id=${resume.id}`;
};

const editResume = async (resume) => {
  if (!isBrowser) return;

  try {
    let fullResumeData = resume;

    // Get full resume data if we only have summary data
    if (!resume.workExperience && !resume.work_experience && !resume.profile_data) {
      try {
        const fullData = await resumeClient.getResume(resume.id);
        fullResumeData = fullData.resume || fullData.data || fullData;
      } catch (err) {
        console.warn("Could not fetch full resume data, using available data:", err);
      }
    }

    // Normalize the data before storing
    const normalizedData = normalizeApiResponse(fullResumeData);

    // Store in localStorage
    saveToStorage(normalizedData, "resumeFormData");
    localStorage.setItem("currentResumeId", resume.id);
    localStorage.setItem("editMode", "true");

    window.location.href = "/builder";
  } catch (err) {
    console.error("Failed to prepare resume for editing:", err);
    showError("Failed to load resume for editing");
  }
};

const duplicateResume = async (resume) => {
  if (!isBrowser) return;

  try {
    const response = await resumeClient.duplicateResume(resume.id);
    success("Resume duplicated successfully");

    // Refresh the list to show the new duplicate
    await fetchResumes(pagination.value?.currentPage || 1);

    // Optionally, scroll to or highlight the new resume
    if (response.id) {
      setTimeout(() => {
        const newResumeCard = document.querySelector(`[data-resume-id="${response.id}"]`);
        if (newResumeCard) {
          newResumeCard.scrollIntoView({ behavior: "smooth", block: "center" });
          newResumeCard.classList.add("ring-2", "ring-green-500");
          setTimeout(() => {
            newResumeCard.classList.remove("ring-2", "ring-green-500");
          }, 3000);
        }
      }, 500);
    }
  } catch (err) {
    console.error("Error duplicating resume:", err);
    showError("Failed to duplicate resume. Please try again.");
  }
};

const exportResume = async (resume) => {
  if (!isBrowser) return;

  try {
    const { blob, filename } = await resumeClient.downloadResume(resume.id, "pdf");

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename || `${resume.title || "resume"}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    success("Resume exported successfully");
  } catch (err) {
    console.error("Error exporting resume:", err);
    showError("Failed to export resume. Please try again.");
  }
};

const shareResume = async (resume) => {
  if (!isBrowser) return;

  try {
    // Check if the API supports sharing (you might want to implement this in ResumeClient)
    let shareUrl;

    try {
      // Try to get a shareable URL from the API
      const response = await resumeClient.shareResume?.(resume.id);
      shareUrl = response.shareUrl || response.url;
    } catch {
      // Fallback to a direct preview URL
      shareUrl = `${window.location.origin}/preview?id=${resume.id}`;
    }

    await navigator.clipboard.writeText(shareUrl);
    success("Share link copied to clipboard!");
  } catch (err) {
    console.error("Error sharing resume:", err);

    // Fallback: try to copy the preview URL directly
    try {
      const fallbackUrl = `${window.location.origin}/preview?id=${resume.id}`;
      await navigator.clipboard.writeText(fallbackUrl);
      success("Share link copied to clipboard!");
    } catch {
      showError("Failed to copy share link. Please try again.");
    }
  }
};

const regenerateContent = async (resume) => {
  if (!isBrowser) return;

  if (!confirm("This will regenerate the AI content for this resume. Continue?")) {
    return;
  }

  try {
    await resumeClient.regenerateContent?.(resume.id);
    success("Resume content regenerated successfully");

    // Refresh the specific resume in the list
    await fetchResumes(pagination.value?.currentPage || 1);
  } catch (err) {
    console.error("Error regenerating content:", err);
    showError("Failed to regenerate content. Please try again.");
  }
};

const handleDeleteResume = async (resume) => {
  if (!isBrowser) return;

  if (!confirm(`Are you sure you want to delete "${resume.title}"?`)) {
    return;
  }

  try {
    await resumeClient.deleteResume(resume.id);
    success("Resume deleted successfully");

    // Remove from local state immediately for better UX
    const index = resumes.value.findIndex((r) => r.id === resume.id);
    if (index > -1) {
      resumes.value.splice(index, 1);
    }

    // Refresh the list to get updated pagination
    if (resumes.value.length === 0 && pagination.value?.currentPage > 1) {
      // If we deleted the last item on this page, go to previous page
      await fetchResumes(pagination.value.currentPage - 1);
    }
  } catch (err) {
    console.error("Error deleting resume:", err);
    showError("Failed to delete resume. Please try again.");

    // Refresh the list to restore the UI state
    await fetchResumes(pagination.value?.currentPage || 1);
  }
};

const changePage = async (page) => {
  if (page < 1 || (pagination.value && page > pagination.value.totalPages)) {
    return;
  }

  await fetchResumes(page);

  // Scroll to top of the resume grid
  document.querySelector(".grid")?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
};

// Lifecycle
onMounted(async () => {
  if (!isBrowser) return;

  try {
    await initAuth();
  } catch (error) {
    console.error("Failed to initialize auth:", error);
    showError("Authentication initialization failed");
  }
});

// Watchers
watch(
  [authInitialized, isAuthenticated],
  ([initialized, authenticated]) => {
    if (!isBrowser) return;

    if (initialized) {
      if (authenticated) {
        fetchResumes();
      } else {
        showError("Please log in to access your resumes");
        setTimeout(() => (window.location.href = "/login"), 2000);
      }
    }
  },
  { immediate: true }
);

// Expose methods for parent components (if needed)
defineExpose({
  fetchResumes,
  clearFormData,
  resumes,
  loading,
  error,
});
</script>

<style scoped>
/* Smooth transition for resume cards */
.grid > * {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

/* Highlight animation for new duplicated resume */
@keyframes highlight {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
  100% {
    transform: scale(1);
  }
}

.highlight-new {
  animation: highlight 0.6s ease;
}
</style>
