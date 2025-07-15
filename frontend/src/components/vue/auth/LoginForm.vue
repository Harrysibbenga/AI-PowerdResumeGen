<template>
  <form @submit.prevent="handleLogin" class="mt-8 space-y-6">
    <BaseInput
      v-model="email"
      label="Email address"
      type="email"
      id="email-address"
      autocomplete="email"
      :disabled="loading"
      required
    />
    <BaseInput
      v-model="password"
      label="Password"
      type="password"
      id="password"
      autocomplete="current-password"
      :disabled="loading"
      required
    />

    <div class="flex items-center justify-between">
      <label class="flex items-center text-sm text-gray-900">
        <input
          type="checkbox"
          v-model="rememberMe"
          :disabled="loading"
          class="h-4 w-4 text-primary-600 border-gray-300 rounded mr-2 disabled:opacity-50"
        />
        Remember me
      </label>
      <a
        href="/forgot-password"
        class="text-sm font-medium text-primary-600 hover:text-primary-500"
      >
        Forgot your password?
      </a>
    </div>

    <BaseButton
      type="submit"
      label="Sign in"
      :loading="loading"
      :disabled="!isFormValid || loading"
      full
    />

    <!-- Error message with better styling -->
    <div v-if="error" class="rounded-md bg-red-50 p-4">
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
          <h3 class="text-sm font-medium text-red-800">Login Error</h3>
          <div class="mt-2 text-sm text-red-700">
            <p>{{ error }}</p>
          </div>
        </div>
      </div>
    </div>
  </form>
</template>

<script setup>
import { ref, computed } from "vue";
import { authClient } from "@/services";
import { useFirebase } from "@/composables/useFirebase";
import { getFirebaseErrorMessage } from "@/utils/getFirebaseErrorMessage";
import { useToast } from "@/composables/useToast";

import BaseInput from "@/components/vue/ui/BaseInput.vue";
import BaseButton from "@/components/vue/ui/BaseButton.vue";

// Form state
const email = ref("");
const password = ref("");
const rememberMe = ref(false);
const error = ref(null);
const loading = ref(false);

// Composables
const { success, error: showError, info } = useToast();
const { initAuth } = useFirebase();

// Computed properties
const isFormValid = computed(() => {
  return email.value.trim() && password.value.trim() && isValidEmail(email.value);
});

// Email validation helper
const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Clear error when user starts typing
const clearError = () => {
  if (error.value) {
    error.value = null;
  }
};

// Watch for input changes to clear errors
import { watch } from "vue";
watch([email, password], clearError);

const handleLogin = async () => {
  // Clear previous errors
  error.value = null;

  // Client-side validation
  if (!isFormValid.value) {
    error.value = "Please enter a valid email and password";
    return;
  }

  loading.value = true;

  try {
    // Ensure Firebase is initialized
    await initAuth();

    console.log("Attempting login for:", email.value);
    const result = await authClient.login(
      email.value.trim(),
      password.value,
      rememberMe.value
    );

    if (result.status === "2fa_required") {
      info("Two-factor authentication required");

      // Store user data for 2FA flow if needed
      sessionStorage.setItem("2fa_user", JSON.stringify(result.user));

      // Navigate using window.location for Astro
      window.location.href = "/2fa";
    } else if (result.status === "success") {
      success("Login successful! Redirecting...");

      // Navigate using window.location with small delay for UX
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 1000);
    } else {
      // Handle any other status
      error.value = "Unexpected login response. Please try again.";
    }
  } catch (err) {
    console.error("Login error:", err);

    // Handle different error types
    let message = "An error occurred during login. Please try again.";

    if (err.response) {
      // API error
      if (err.response.status === 401) {
        message = "Invalid email or password";
      } else if (err.response.status === 429) {
        message = "Too many login attempts. Please try again later.";
      } else if (err.response.data?.detail) {
        message = err.response.data.detail;
      }
    } else if (err.code) {
      // Firebase error
      message = getFirebaseErrorMessage(err);
    }

    showError(message);
    error.value = message;
  } finally {
    loading.value = false;
  }
};

// Handle form reset (optional)
const resetForm = () => {
  email.value = "";
  password.value = "";
  rememberMe.value = false;
  error.value = null;
};

// Expose methods if needed by parent component
defineExpose({
  resetForm,
});
</script>
