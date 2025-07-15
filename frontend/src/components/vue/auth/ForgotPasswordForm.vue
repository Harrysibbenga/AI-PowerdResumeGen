<template>
  <div class="fade-in">
    <!-- Success State -->
    <div v-if="isSuccess" class="text-center">
      <div
        class="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-green-100 mb-4"
      >
        <svg
          class="h-8 w-8 text-green-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M5 13l4 4L19 7"
          />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">Check your email</h3>
      <p class="text-sm text-gray-600 mb-6">
        If an account with email <strong>{{ submittedEmail }}</strong> exists, you will
        receive a password reset link shortly.
      </p>
      <div class="space-y-3">
        <BaseButton
          @click="resetForm"
          label="Send another email"
          variant="outline"
          class="mb-3"
          full
        />
        <BaseButton @click="goToLogin" label="Back to sign in" full />
      </div>
    </div>

    <!-- Form State -->
    <form v-else @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Email Input -->
      <BaseInput
        v-model="email"
        label="Email address"
        type="email"
        id="email"
        autocomplete="email"
        :disabled="isLoading"
        required
        placeholder="Enter your email address"
      />

      <!-- Submit Button -->
      <BaseButton
        type="submit"
        :label="isLoading ? 'Sending reset link...' : 'Send reset link'"
        :loading="isLoading"
        :disabled="!isFormValid || isLoading"
        full
      />

      <!-- General Error -->
      <div v-if="generalError" class="rounded-md bg-red-50 p-4">
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
            <h3 class="text-sm font-medium text-red-800">Error</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ generalError }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Rate Limiting Notice -->
      <div v-if="showRateLimit" class="rounded-md bg-yellow-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path
                fill-rule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-yellow-800">Rate Limited</h3>
            <div class="mt-2 text-sm text-yellow-700">
              <p>Too many requests. Please wait before trying again.</p>
            </div>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { authClient } from "@/services";
import { useToast } from "@/composables/useToast";

import BaseInput from "@/components/vue/ui/BaseInput.vue";
import BaseButton from "@/components/vue/ui/BaseButton.vue";

// Form state
const email = ref("");
const isLoading = ref(false);
const isSuccess = ref(false);
const submittedEmail = ref("");

// Error state
const generalError = ref("");
const showRateLimit = ref(false);

// Composables
const { success, error: showError, info } = useToast();

// Computed properties
const isFormValid = computed(() => {
  return email.value.trim() && isValidEmail(email.value);
});

// Email validation
const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Clear errors when user types
const clearErrors = () => {
  if (generalError.value) {
    generalError.value = "";
  }
  if (showRateLimit.value) {
    showRateLimit.value = false;
  }
};

// Watch email for validation
watch(email, clearErrors);

// Navigation helper
const goToLogin = () => {
  window.location.href = "/login";
};

// Handle form submission
const handleSubmit = async () => {
  // Clear previous errors
  clearErrors();

  if (!isFormValid.value) {
    generalError.value = "Please enter a valid email address";
    return;
  }

  isLoading.value = true;

  try {
    console.log("Requesting password reset for:", email.value);

    const result = await authClient.forgotPassword(email.value.trim());

    // Show success state
    submittedEmail.value = email.value;
    isSuccess.value = true;

    // Show toast notification
    success("Password reset link sent!");

    console.log("Password reset request successful");
  } catch (err) {
    console.error("Forgot password error:", err);

    // Handle different error types
    if (err.response?.status === 429) {
      showRateLimit.value = true;
      showError("Too many requests. Please wait before trying again.");
    } else if (err.response?.status === 400) {
      generalError.value =
        err.response.data?.detail || "Invalid request. Please check your email address.";
    } else if (err.response?.data?.detail) {
      generalError.value = err.response.data.detail;
    } else {
      generalError.value = "An error occurred. Please try again later.";
    }

    showError(generalError.value);
  } finally {
    isLoading.value = false;
  }
};

// Reset form to initial state
const resetForm = () => {
  email.value = "";
  isSuccess.value = false;
  submittedEmail.value = "";
  generalError.value = "";
  showRateLimit.value = false;
  isLoading.value = false;
};

// Clear form on component mount
resetForm();
</script>

<style scoped>
/* Animation classes */
.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
