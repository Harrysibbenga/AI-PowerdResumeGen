<template>
  <div class="bg-white rounded-lg shadow p-6 mb-8">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">Your Resumes</h2>
      <a
        href="/builder"
        class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors"
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
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"
        ></div>
        <span class="ml-2 text-gray-600">
          {{ !authInitialized ? "Initializing..." : "Loading resumes..." }}
        </span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="col-span-full">
        <div class="border border-red-200 rounded-lg p-6 bg-red-50">
          <p class="text-red-600 text-center">{{ error }}</p>
          <button
            @click="fetchResumes"
            class="mt-4 w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <NoResumesFound v-else-if="resumes.length === 0" />

      <!-- Resume Grid -->
      <ResumeCard
        v-else
        v-for="resume in resumes"
        :key="resume.id"
        :resume="resume"
        @delete="handleDeleteResume"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";
import NoResumesFound from "./NoResumesFound.vue";
import ResumeCard from "./ResumeCard.vue";

const resumes = ref([]);
const loading = ref(false);
const error = ref(null);

const { user, isAuthenticated, authInitialized, initAuth, waitForAuth } = useFirebase();
const { success, error: showError } = useToast();

const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

const fetchResumes = async () => {
  try {
    loading.value = true;
    error.value = null;

    // Wait for authentication
    const currentUser = await waitForAuth();

    if (!currentUser) {
      showError("Please log in to view your resumes");
      setTimeout(() => (window.location.href = "/login"), 1500);
      return;
    }

    // Get fresh token
    const idToken = await currentUser.getIdToken();

    const response = await fetch(`${API_URL}/api/v1/resume`, {
      headers: {
        Authorization: `Bearer ${idToken}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        showError("Session expired. Please log in again.");
        setTimeout(() => (window.location.href = "/login"), 1500);
        return;
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    resumes.value = Array.isArray(data) ? data : data.resumes || [];
  } catch (err) {
    console.error("Error fetching resumes:", err);
    error.value = err.message || "Failed to load resumes";
    showError("Failed to load resumes");
  } finally {
    loading.value = false;
  }
};

const handleDeleteResume = async (resumeId) => {
  if (!confirm("Are you sure you want to delete this resume?")) {
    return;
  }

  try {
    const currentUser = await waitForAuth();
    if (!currentUser) {
      showError("Please log in to delete resumes");
      return;
    }

    const idToken = await currentUser.getIdToken();

    const response = await fetch(`${API_URL}/api/v1/resume/${resumeId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${idToken}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // Remove from local state
    resumes.value = resumes.value.filter((resume) => resume.id !== resumeId);
    success("Resume deleted successfully");
  } catch (err) {
    console.error("Error deleting resume:", err);
    showError("Failed to delete resume. Please try again.");
  }
};

// Initialize auth and watch for changes
onMounted(async () => {
  try {
    await initAuth();
  } catch (error) {
    console.error("Failed to initialize auth:", error);
    showError("Authentication initialization failed");
  }
});

// Watch for authentication state changes
watch(
  [authInitialized, isAuthenticated],
  ([initialized, authenticated]) => {
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
