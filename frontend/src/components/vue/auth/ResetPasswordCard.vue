<template>
  <div class="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-md">
    <!-- Debug: Show token (remove in production) -->
    <div
      v-if="currentToken"
      class="text-xs text-gray-500 bg-gray-100 p-2 rounded font-mono break-all"
    >
      Token: {{ currentToken }}
    </div>

    <!-- Token Validation Message -->
    <div v-if="!currentToken" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Invalid Reset Link</h3>
          <div class="mt-2 text-sm text-red-700">
            <p>
              This reset link is invalid or has expired. Please request a new password
              reset.
            </p>
          </div>
          <div class="mt-4">
            <a
              href="/forgot-password"
              class="text-sm font-medium text-red-800 underline hover:text-red-900"
            >
              Request new reset link →
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Valid Token Content -->
    <div v-else>
      <div>
        <div
          class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100 mb-6"
        >
          <svg
            class="h-6 w-6 text-primary-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-3.586l6.293-6.293A6 6 0 0121 9z"
            />
          </svg>
        </div>
        <h1 class="text-center text-3xl font-extrabold text-gray-900">
          Reset your password
        </h1>
        <p class="mt-2 text-center text-sm text-gray-600">
          Enter your new password below to complete the reset process.
        </p>
        <p class="mt-2 text-center text-sm text-gray-600">
          Or
          <a href="/login" class="font-medium text-primary-600 hover:text-primary-500">
            back to sign in
          </a>
        </p>
      </div>

      <ResetPasswordForm :token="currentToken" />

      <!-- Security Notice -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path
                fill-rule="evenodd"
                d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-blue-800">Security tip</h3>
            <div class="mt-2 text-sm text-blue-700">
              <p>
                Choose a strong password with at least 8 characters, including uppercase
                and lowercase letters, numbers, and special characters.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import ResetPasswordForm from "@/components/vue/auth/ResetPasswordForm.vue";

const props = defineProps({
  token: {
    type: String,
    default: null,
  },
});

const currentToken = ref(props.token);

// Function to handle token from client-side
const handleTokenEvent = (event) => {
  console.log("Received token event:", event.detail);
  currentToken.value = event.detail.token;
};

// Function to extract token from URL directly
const extractTokenFromURL = () => {
  if (typeof window !== "undefined") {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token");
    console.log("Vue component extracted token:", token);
    if (token) {
      currentToken.value = token;
    }
  }
};

onMounted(() => {
  // Try to extract token from URL if not provided as prop
  if (!currentToken.value) {
    extractTokenFromURL();
  }

  // Listen for token events from parent page
  window.addEventListener("resetPasswordToken", handleTokenEvent);

  console.log("ResetPasswordCard mounted with token:", currentToken.value);
});

onUnmounted(() => {
  window.removeEventListener("resetPasswordToken", handleTokenEvent);
});
</script>
