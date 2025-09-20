<!-- ResumeAccessGate.vue -->
<template>
  <div>
    <div v-if="isLoading" class="text-center py-8">
      <div
        class="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent mx-auto mb-4"
      ></div>
      <p class="text-gray-600">Loading...</p>
    </div>

    <div v-else-if="isAuthenticated">
      <ResumeForm />
    </div>

    <div v-else class="py-12 text-center">
      <div
        class="max-w-md mx-auto bg-white rounded-lg p-8 border border-gray-200 shadow-sm"
      >
        <div class="text-blue-600 mb-4">
          <svg
            class="w-12 h-12 mx-auto"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            ></path>
          </svg>
        </div>
        <h2 class="text-2xl font-bold mb-4 text-gray-900">Login Required</h2>
        <p class="text-gray-600 mb-6">
          Please log in to create and save your resume securely.
        </p>
        <div class="flex flex-col sm:flex-row justify-center gap-3">
          <button
            @click="navigateToLogin"
            class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            Log In
          </button>
          <button
            @click="navigateToRegister"
            class="px-6 py-2 border border-blue-600 text-blue-600 hover:bg-blue-50 rounded-lg font-medium transition-colors"
          >
            Register
          </button>
        </div>
        <p class="text-xs text-gray-500 mt-4">
          Your resume data will be securely stored and accessible from any device.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import ResumeForm from "@/components/vue/resume/form/ResumeForm.vue";
import { useFirebase } from "@/composables/useFirebase";

const { user, isLoading, isAuthenticated, initAuth } = useFirebase();

// Check if we're in browser environment
const isBrowser = typeof window !== "undefined";

const navigateToLogin = () => {
  if (isBrowser) {
    window.location.href = "/login";
  }
};

const navigateToRegister = () => {
  if (isBrowser) {
    window.location.href = "/register";
  }
};

// Initialize auth only in browser
onMounted(() => {
  if (isBrowser) {
    initAuth(); // Start listening on mount
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
