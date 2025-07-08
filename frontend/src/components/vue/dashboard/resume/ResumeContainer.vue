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
      <!-- Authentication Loading State -->
      <div
        v-if="isAuthLoading || !authInitialized"
        class="col-span-full flex justify-center items-center py-12"
      >
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"
        ></div>
        <span class="ml-2 text-gray-600">Checking authentication...</span>
      </div>

      <!-- Resume Loading State -->
      <div
        v-else-if="loading"
        class="col-span-full flex justify-center items-center py-12"
      >
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"
        ></div>
        <span class="ml-2 text-gray-600">Loading resumes...</span>
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
      <NoResumesFound v-else-if="!loading && resumes.length === 0" />

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

<script>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import NoResumesFound from "./NoResumesFound.vue";
import ResumeCard from "./ResumeCard.vue";

export default {
  name: "ResumeContainer",
  components: {
    NoResumesFound,
    ResumeCard,
  },
  setup() {
    const resumes = ref([]);
    const loading = ref(false); // Start with false since auth loading handles initial state
    const error = ref(null);

    const {
      user,
      isLoading: isAuthLoading,
      isAuthenticated,
      authInitialized,
      initAuth,
      getFirebaseAuth,
      waitForAuth,
      cleanup,
    } = useFirebase();

    const fetchResumes = async () => {
      try {
        console.log("Starting to fetch resumes...");
        loading.value = true;
        error.value = null;

        // Wait for authentication to be ready
        const currentUser = await waitForAuth();
        console.log("Auth ready, user:", currentUser ? "logged in" : "not logged in");

        if (!currentUser) {
          console.log("No user found, redirecting to login");
          window.location.href = "/login";
          return;
        }

        const auth = await getFirebaseAuth();
        const idToken = await currentUser.getIdToken();
        const API_URL = import.meta.env.VITE_API_URL || import.meta.env.PUBLIC_API_URL;

        console.log("Making API request to:", `${API_URL}/api/v1/resumes`);

        const response = await fetch(`${API_URL}/api/v1/resumes`, {
          headers: {
            Authorization: `Bearer ${idToken}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch resumes: ${response.status}`);
        }

        const data = await response.json();
        console.log("Resumes fetched:", data);
        resumes.value = data || [];
      } catch (err) {
        console.error("Error fetching resumes:", err);
        error.value = err.message || "Failed to load resumes";

        // If user is not authenticated, redirect to login
        if (err.message.includes("Not logged in")) {
          window.location.href = "/login";
        }
      } finally {
        loading.value = false;
        console.log("Fetch resumes completed");
      }
    };

    const handleDeleteResume = async (resumeId) => {
      try {
        const currentUser = await waitForAuth();
        if (!currentUser) return;

        const auth = await getFirebaseAuth();
        const idToken = await currentUser.getIdToken();
        const API_URL = import.meta.env.VITE_API_URL || import.meta.env.PUBLIC_API_URL;

        const response = await fetch(`${API_URL}/api/v1/resumes/${resumeId}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${idToken}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error("Failed to delete resume");
        }

        // Remove from local state
        resumes.value = resumes.value.filter((resume) => resume.id !== resumeId);
      } catch (err) {
        console.error("Error deleting resume:", err);
        alert("Failed to delete resume. Please try again.");
      }
    };

    // Watch for authentication changes
    watch(
      [authInitialized, isAuthenticated],
      ([initialized, authenticated]) => {
        console.log(
          "Auth state watch triggered - initialized:",
          initialized,
          "authenticated:",
          authenticated
        );

        if (initialized) {
          if (authenticated) {
            console.log("User is authenticated, fetching resumes");
            fetchResumes();
          } else {
            console.log("User not authenticated, redirecting to login");
            window.location.href = "/login";
          }
        }
      },
      { immediate: true }
    );

    onMounted(async () => {
      console.log("ResumeContainer mounted, initializing auth...");
      await initAuth();
    });

    onUnmounted(() => {
      cleanup();
    });

    return {
      resumes,
      loading,
      error,
      fetchResumes,
      handleDeleteResume,
      isAuthLoading,
      isAuthenticated,
      authInitialized,
    };
  },
};
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
