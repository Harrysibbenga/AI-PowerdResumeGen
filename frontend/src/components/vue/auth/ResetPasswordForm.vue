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
      <h3 class="text-lg font-medium text-gray-900 mb-2">Password reset successful!</h3>
      <p class="text-sm text-gray-600 mb-6">
        Your password has been successfully updated. You can now sign in with your new
        password.
      </p>
      <BaseButton @click="goToLogin" label="Continue to sign in" full />
    </div>

    <!-- Form State -->
    <form v-else @submit.prevent="handleSubmit" class="space-y-6">
      <!-- New Password -->
      <div>
        <label for="new-password" class="block text-sm font-medium text-gray-700 mb-2">
          New Password
        </label>
        <div class="relative">
          <input
            :type="showNewPassword ? 'text' : 'password'"
            id="new-password"
            v-model="newPassword"
            @input="validatePasswordStrength"
            :disabled="isLoading"
            autocomplete="new-password"
            required
            class="appearance-none relative block w-full px-3 py-2 pr-10 border rounded-md placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm transition-colors"
            :class="{
              'border-gray-300': !errors.newPassword,
              'border-red-500 bg-red-50': errors.newPassword,
              'opacity-50 cursor-not-allowed': isLoading,
            }"
            placeholder="Enter your new password"
          />
          <button
            type="button"
            @click="showNewPassword = !showNewPassword"
            :disabled="isLoading"
            class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <svg
              v-if="showNewPassword"
              class="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
              />
            </svg>
            <svg
              v-else
              class="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
          </button>
        </div>

        <!-- Password Strength Indicator -->
        <div v-if="newPassword && passwordStrength" class="mt-2">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs text-gray-600">Password Strength</span>
            <span class="text-xs font-medium" :class="strengthColor">
              {{ passwordStrength.strength }}
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all duration-300"
              :class="strengthBarColor"
              :style="{ width: `${(passwordStrength.score / 5) * 100}%` }"
            ></div>
          </div>
          <ul
            v-if="passwordStrength.suggestions.length > 0"
            class="mt-2 text-xs text-gray-600"
          >
            <li
              v-for="suggestion in passwordStrength.suggestions"
              :key="suggestion"
              class="flex items-start"
            >
              <span class="text-red-500 mr-1">•</span>
              {{ suggestion }}
            </li>
          </ul>
        </div>

        <p v-if="errors.newPassword" class="mt-1 text-sm text-red-600">
          {{ errors.newPassword }}
        </p>
      </div>

      <!-- Confirm Password -->
      <div>
        <label
          for="confirm-password"
          class="block text-sm font-medium text-gray-700 mb-2"
        >
          Confirm New Password
        </label>
        <div class="relative">
          <input
            :type="showConfirmPassword ? 'text' : 'password'"
            id="confirm-password"
            v-model="confirmPassword"
            @blur="validatePasswordMatch"
            :disabled="isLoading"
            autocomplete="new-password"
            required
            class="appearance-none relative block w-full px-3 py-2 pr-10 border rounded-md placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm transition-colors"
            :class="{
              'border-gray-300': !errors.confirmPassword,
              'border-red-500 bg-red-50': errors.confirmPassword,
              'opacity-50 cursor-not-allowed': isLoading,
            }"
            placeholder="Confirm your new password"
          />
          <button
            type="button"
            @click="showConfirmPassword = !showConfirmPassword"
            :disabled="isLoading"
            class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <svg
              v-if="showConfirmPassword"
              class="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
              />
            </svg>
            <svg
              v-else
              class="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
          </button>
        </div>
        <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-600">
          {{ errors.confirmPassword }}
        </p>
      </div>

      <!-- Submit Button -->
      <BaseButton
        type="submit"
        :label="isLoading ? 'Resetting password...' : 'Reset password'"
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
            <h3 class="text-sm font-medium text-red-800">Reset Error</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ generalError }}</p>
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

import BaseButton from "@/components/vue/ui/BaseButton.vue";

const props = defineProps({
  token: {
    type: String,
    required: true,
  },
});

// Form state
const newPassword = ref("");
const confirmPassword = ref("");
const isLoading = ref(false);
const isSuccess = ref(false);

// UI state
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

// Validation state
const errors = ref({
  newPassword: "",
  confirmPassword: "",
});
const generalError = ref("");
const passwordStrength = ref(null);

// Composables
const { success, error: showError } = useToast();

// Debounced password strength validation
let strengthTimeout = null;

const validatePasswordStrength = async () => {
  if (!newPassword.value) {
    passwordStrength.value = null;
    return;
  }

  // Clear previous timeout
  if (strengthTimeout) {
    clearTimeout(strengthTimeout);
  }

  // Debounce the API call
  strengthTimeout = setTimeout(async () => {
    try {
      passwordStrength.value = await authClient.validatePasswordStrength(
        newPassword.value
      );

      // Clear new password error if password is now strong
      if (passwordStrength.value.is_strong) {
        errors.value.newPassword = "";
      }
    } catch (error) {
      console.error("Password strength validation error:", error);
    }
  }, 300);
};

const validatePasswordMatch = () => {
  if (confirmPassword.value && newPassword.value !== confirmPassword.value) {
    errors.value.confirmPassword = "Passwords do not match";
  } else {
    errors.value.confirmPassword = "";
  }
};

// Computed properties
const strengthColor = computed(() => {
  if (!passwordStrength.value) return "text-gray-500";

  const strength = passwordStrength.value.strength;
  switch (strength) {
    case "Very Weak":
      return "text-red-600";
    case "Weak":
      return "text-red-500";
    case "Fair":
      return "text-yellow-500";
    case "Good":
      return "text-blue-500";
    case "Strong":
      return "text-green-500";
    case "Very Strong":
      return "text-green-600";
    default:
      return "text-gray-500";
  }
});

const strengthBarColor = computed(() => {
  if (!passwordStrength.value) return "bg-gray-300";

  const strength = passwordStrength.value.strength;
  switch (strength) {
    case "Very Weak":
      return "bg-red-600";
    case "Weak":
      return "bg-red-500";
    case "Fair":
      return "bg-yellow-500";
    case "Good":
      return "bg-blue-500";
    case "Strong":
      return "bg-green-500";
    case "Very Strong":
      return "bg-green-600";
    default:
      return "bg-gray-300";
  }
});

const isFormValid = computed(() => {
  return (
    newPassword.value &&
    confirmPassword.value &&
    newPassword.value === confirmPassword.value &&
    passwordStrength.value?.is_strong &&
    !Object.values(errors.value).some((error) => error)
  );
});

// Methods
const clearErrors = () => {
  errors.value = {
    newPassword: "",
    confirmPassword: "",
  };
  generalError.value = "";
};

const goToLogin = () => {
  window.location.href = "/login";
};

const handleSubmit = async () => {
  clearErrors();

  // Client-side validation
  if (!newPassword.value) {
    errors.value.newPassword = "New password is required";
    return;
  }

  if (!confirmPassword.value) {
    errors.value.confirmPassword = "Password confirmation is required";
    return;
  }

  if (newPassword.value !== confirmPassword.value) {
    errors.value.confirmPassword = "Passwords do not match";
    return;
  }

  if (!passwordStrength.value?.is_strong) {
    errors.value.newPassword = "Password does not meet security requirements";
    return;
  }

  isLoading.value = true;

  try {
    const result = await authClient.resetPassword(props.token, newPassword.value);

    if (result.message) {
      // Clear form
      newPassword.value = "";
      confirmPassword.value = "";
      passwordStrength.value = null;

      success(result.message);
      isSuccess.value = true;
    }
  } catch (error) {
    console.error("Reset password error:", error);

    // Handle specific error cases
    if (error.response?.status === 400) {
      if (error.response.data?.detail?.includes("token")) {
        generalError.value =
          "This reset link has expired or is invalid. Please request a new password reset.";
      } else if (error.response.data?.suggestions) {
        errors.value.newPassword = error.response.data.suggestions.join(", ");
      } else {
        generalError.value = error.response.data?.detail || "Invalid request";
      }
    } else if (error.response?.data?.detail) {
      generalError.value = error.response.data.detail;
    } else {
      generalError.value = "An unexpected error occurred. Please try again.";
    }

    showError(generalError.value);
  } finally {
    isLoading.value = false;
  }
};

// Watch for password changes to validate match
watch([newPassword, confirmPassword], () => {
  if (confirmPassword.value) {
    validatePasswordMatch();
  }
});

// Cleanup timeout on unmount
import { onUnmounted } from "vue";
onUnmounted(() => {
  if (strengthTimeout) {
    clearTimeout(strengthTimeout);
  }
});
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
