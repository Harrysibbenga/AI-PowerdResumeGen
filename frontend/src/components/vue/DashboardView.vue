<template>
  <div v-if="authInitialized">
    <div v-if="isAuthenticated" class="min-h-[calc(100vh-300px)] py-12 px-4">
      <div class="container mx-auto max-w-7xl">
        <h1 class="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        <ResumeContainer />

        <AccountSettings
          :user="user"
          @update-success="handleSuccess"
          @update-error="handleError"
        />
      </div>
    </div>
    <div v-else class="min-h-screen flex items-center justify-center">
      <div class="text-center">
        <div
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"
        ></div>
        <p class="text-gray-500">Redirecting to login...</p>
      </div>
    </div>
  </div>
  <div v-else class="min-h-screen flex items-center justify-center">
    <div class="text-center">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"
      ></div>
      <p class="text-gray-500">Initializing authentication...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import ResumeContainer from "@/components/vue/dashboard/resume/ResumeContainer.vue";
import AccountSettings from "@/components/vue/dashboard/AccountSettings.vue";
import { useToast } from "@/composables/useToast";

const { initAuth, user, isAuthenticated, authInitialized } = useFirebase();
const { success, error: showError, info } = useToast();

// Check if we're in browser environment
const isBrowser = typeof window !== "undefined";

// Initialize auth when component mounts
onMounted(async () => {
  // Only initialize in browser
  if (!isBrowser) return;

  try {
    await initAuth();

    // Debug info
    console.log("Dashboard - Auth initialized:", authInitialized.value);
    console.log("Dashboard - Is authenticated:", isAuthenticated.value);
    console.log("Dashboard - User:", user.value);
  } catch (error) {
    console.error("Dashboard - Auth initialization failed:", error);
    showError("Failed to initialize authentication");
  }
});

// Watch for authentication changes and redirect if needed
watch(
  [authInitialized, isAuthenticated],
  ([initialized, authenticated]) => {
    // Only handle redirects in browser
    if (!isBrowser) return;

    if (initialized && !authenticated) {
      info("Please log in to access the dashboard");
      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);
    }
  },
  { immediate: true }
);

const handleSuccess = (msg) => {
  success(msg);
};

const handleError = (msg) => {
  showError(msg);
};
</script>
