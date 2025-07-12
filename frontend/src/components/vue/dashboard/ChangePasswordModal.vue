<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Change Password</h3>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-4">
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"
        ></div>
        <p class="text-gray-600 mt-2">Changing password...</p>
      </div>

      <!-- Form -->
      <form v-else @submit.prevent="handleChangePassword">
        <!-- Current Password -->
        <div class="mb-4">
          <label
            for="current-password"
            class="block text-sm font-medium text-gray-700 mb-2"
          >
            Current Password
          </label>
          <div class="relative">
            <input
              :type="showCurrentPassword ? 'text' : 'password'"
              v-model="currentPassword"
              id="current-password"
              class="w-full px-3 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              :class="errors.currentPassword ? 'border-red-500' : 'border-gray-300'"
              placeholder="Enter current password"
              required
            />
            <button
              type="button"
              @click="showCurrentPassword = !showCurrentPassword"
              class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-400 hover:text-gray-600"
            >
              <svg
                v-if="showCurrentPassword"
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
          <p v-if="errors.currentPassword" class="mt-1 text-sm text-red-600">
            {{ errors.currentPassword }}
          </p>
        </div>

        <!-- New Password -->
        <div class="mb-4">
          <label for="new-password" class="block text-sm font-medium text-gray-700 mb-2">
            New Password
          </label>
          <div class="relative">
            <input
              :type="showNewPassword ? 'text' : 'password'"
              v-model="newPassword"
              id="new-password"
              @input="validatePasswordStrength"
              class="w-full px-3 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              :class="errors.newPassword ? 'border-red-500' : 'border-gray-300'"
              placeholder="Enter new password"
              required
            />
            <button
              type="button"
              @click="showNewPassword = !showNewPassword"
              class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-400 hover:text-gray-600"
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
        <div class="mb-6">
          <label
            for="confirm-password"
            class="block text-sm font-medium text-gray-700 mb-2"
          >
            Confirm New Password
          </label>
          <div class="relative">
            <input
              :type="showConfirmPassword ? 'text' : 'password'"
              v-model="confirmPassword"
              id="confirm-password"
              @blur="validatePasswordMatch"
              class="w-full px-3 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              :class="errors.confirmPassword ? 'border-red-500' : 'border-gray-300'"
              placeholder="Confirm new password"
              required
            />
            <button
              type="button"
              @click="showConfirmPassword = !showConfirmPassword"
              class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-400 hover:text-gray-600"
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

        <!-- General Error Message -->
        <div
          v-if="generalError"
          class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg"
        >
          <p class="text-sm text-red-800">{{ generalError }}</p>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-3">
          <button
            type="button"
            @click="handleCancel"
            :disabled="isLoading"
            class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading">Changing...</span>
            <span v-else>Change Password</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { authClient } from "@/services";

const props = defineProps({
  user: Object,
});

const emit = defineEmits(["close", "success", "error"]);

// Form fields
const currentPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

// UI state
const isLoading = ref(false);
const showCurrentPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

// Validation state
const errors = ref({
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
});
const generalError = ref("");
const passwordStrength = ref(null);

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
    currentPassword.value &&
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
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  };
  generalError.value = "";
};

const handleChangePassword = async () => {
  clearErrors();

  // Client-side validation
  if (!currentPassword.value) {
    errors.value.currentPassword = "Current password is required";
    return;
  }

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

  if (currentPassword.value === newPassword.value) {
    errors.value.newPassword = "New password must be different from current password";
    return;
  }

  if (!passwordStrength.value?.is_strong) {
    errors.value.newPassword = "Password does not meet security requirements";
    return;
  }

  isLoading.value = true;

  try {
    const result = await authClient.completePasswordChange(
      currentPassword.value,
      newPassword.value,
      confirmPassword.value
    );

    if (result.success) {
      // Clear form
      currentPassword.value = "";
      newPassword.value = "";
      confirmPassword.value = "";
      passwordStrength.value = null;

      emit("success", result.message);
      emit("close");
    } else {
      // Handle validation errors
      if (result.errors && result.errors.length > 0) {
        // Check if it's a current password error
        if (result.message.toLowerCase().includes("current password")) {
          errors.value.currentPassword = result.message;
        } else {
          // Show as general error or new password error
          errors.value.newPassword = result.errors.join(", ");
        }
      } else {
        generalError.value = result.message;
      }
    }
  } catch (error) {
    console.error("Password change error:", error);

    // Handle specific error cases
    if (error.response?.status === 401) {
      errors.value.currentPassword = "Current password is incorrect";
    } else if (error.response?.data?.detail) {
      generalError.value = error.response.data.detail;
    } else {
      generalError.value = "An unexpected error occurred. Please try again.";
    }
  } finally {
    isLoading.value = false;
  }
};

const handleCancel = () => {
  if (!isLoading.value) {
    emit("close");
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
