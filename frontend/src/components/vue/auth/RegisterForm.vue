<template>
  <form @submit.prevent="handleRegister" class="space-y-6">
    <!-- Error Display -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-600 text-sm">{{ error }}</p>
    </div>

    <BaseInput
      v-model="email"
      type="email"
      label="Email Address"
      id="register-email"
      autocomplete="email"
      placeholder="Enter your email address"
      required
      :disabled="loading"
    />

    <BaseInput
      v-model="displayName"
      type="text"
      label="Full Name"
      id="display-name"
      autocomplete="name"
      placeholder="Enter your full name"
      required
      :disabled="loading"
    />

    <BaseInput
      v-model="password"
      type="password"
      label="Password"
      id="register-password"
      autocomplete="new-password"
      placeholder="Create a password (min. 6 characters)"
      required
      :disabled="loading"
    />

    <BaseInput
      v-model="confirmPassword"
      type="password"
      label="Confirm Password"
      id="confirm-password"
      autocomplete="new-password"
      placeholder="Confirm your password"
      required
      :disabled="loading"
    />

    <!-- Password Strength Indicator -->
    <div v-if="password" class="space-y-2">
      <div class="text-sm text-gray-600">Password strength:</div>
      <div class="flex space-x-1">
        <div
          v-for="i in 4"
          :key="i"
          class="h-2 w-1/4 rounded"
          :class="getPasswordStrengthColor(i)"
        ></div>
      </div>
      <div class="text-xs" :class="passwordStrengthTextColor">
        {{ passwordStrengthText }}
      </div>
    </div>

    <!-- Terms and Conditions -->
    <div class="flex items-start">
      <input
        id="agree-terms"
        v-model="agreed"
        type="checkbox"
        class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 mt-0.5"
        :disabled="loading"
        required
      />
      <label for="agree-terms" class="ml-3 block text-sm text-gray-900">
        I agree to the
        <a
          href="/terms"
          target="_blank"
          class="text-primary-600 hover:text-primary-500 underline"
        >
          Terms of Service
        </a>
        and
        <a
          href="/privacy"
          target="_blank"
          class="text-primary-600 hover:text-primary-500 underline"
        >
          Privacy Policy
        </a>
      </label>
    </div>

    <!-- Submit Button -->
    <BaseButton
      type="submit"
      :label="loading ? 'Creating Account...' : 'Create Account'"
      :loading="loading"
      :disabled="!isFormValid || loading"
      full
    />

    <!-- Login Link -->
    <div class="text-center">
      <p class="text-sm text-gray-600">
        Already have an account?
        <a href="/login" class="font-medium text-primary-600 hover:text-primary-500">
          Sign in
        </a>
      </p>
    </div>
  </form>
</template>

<script setup>
import { ref, computed } from "vue";
import { createUserWithEmailAndPassword, updateProfile } from "firebase/auth";
import { getFirebaseErrorMessage } from "@/utils/getFirebaseErrorMessage";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";

import BaseInput from "@/components/vue/ui/BaseInput.vue";
import BaseButton from "@/components/vue/ui/BaseButton.vue";

const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const displayName = ref("");
const agreed = ref(false);
const loading = ref(false);
const error = ref(null);

const { initAuth, getAuth } = useFirebase();
const { success, error: showError } = useToast();

const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

// Computed properties
const passwordStrength = computed(() => {
  const pwd = password.value;
  if (!pwd) return 0;

  let strength = 0;
  if (pwd.length >= 6) strength++;
  if (pwd.length >= 8) strength++;
  if (/[A-Z]/.test(pwd) && /[a-z]/.test(pwd)) strength++;
  if (/\d/.test(pwd) && /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd)) strength++;

  return strength;
});

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value;
  if (strength === 0) return "Too weak";
  if (strength === 1) return "Weak";
  if (strength === 2) return "Fair";
  if (strength === 3) return "Good";
  return "Strong";
});

const passwordStrengthTextColor = computed(() => {
  const strength = passwordStrength.value;
  if (strength === 0) return "text-red-500";
  if (strength === 1) return "text-orange-500";
  if (strength === 2) return "text-yellow-500";
  if (strength === 3) return "text-blue-500";
  return "text-green-500";
});

const passwordsMatch = computed(() => {
  return !confirmPassword.value || password.value === confirmPassword.value;
});

const isFormValid = computed(() => {
  return (
    email.value.trim() &&
    displayName.value.trim() &&
    password.value.length >= 6 &&
    passwordsMatch.value &&
    agreed.value
  );
});

// Methods
const getPasswordStrengthColor = (index) => {
  const strength = passwordStrength.value;
  if (index <= strength) {
    if (strength === 1) return "bg-red-400";
    if (strength === 2) return "bg-yellow-400";
    if (strength === 3) return "bg-blue-400";
    if (strength === 4) return "bg-green-400";
  }
  return "bg-gray-200";
};

const validateForm = () => {
  error.value = null;

  // Check email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.value)) {
    error.value = "Please enter a valid email address";
    showError("Please enter a valid email address");
    return false;
  }

  // Check display name
  if (displayName.value.trim().length < 2) {
    error.value = "Display name must be at least 2 characters long";
    showError("Display name must be at least 2 characters long");
    return false;
  }

  // Check password strength
  if (password.value.length < 6) {
    error.value = "Password must be at least 6 characters long";
    showError("Password must be at least 6 characters long");
    return false;
  }

  // Check if passwords match
  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match";
    showError("Passwords do not match");
    return false;
  }

  // Check if terms are agreed
  if (!agreed.value) {
    error.value = "You must agree to the Terms of Service and Privacy Policy";
    showError("You must agree to the Terms of Service and Privacy Policy");
    return false;
  }

  return true;
};

const handleRegister = async () => {
  if (!validateForm()) {
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    // Initialize Firebase auth
    await initAuth();
    const auth = await getAuth();

    if (!auth) {
      throw new Error("Authentication service not available. Please try again.");
    }

    console.log("Creating Firebase user...");

    // Create user account in Firebase
    const userCredential = await createUserWithEmailAndPassword(
      auth,
      email.value.trim(),
      password.value
    );

    console.log("Firebase user created:", userCredential.user.uid);

    // Update user profile with display name
    await updateProfile(userCredential.user, {
      displayName: displayName.value.trim(),
    });

    console.log("Profile updated, getting ID token...");

    // Get ID token for backend registration
    const idToken = await userCredential.user.getIdToken();

    console.log("Registering with backend...");

    // Register with backend
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_token: idToken,
        display_name: displayName.value.trim(),
      }),
    });

    console.log("Backend response status:", response.status);

    if (!response.ok) {
      let errorMessage = "Registration failed";
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch (e) {
        console.error("Error parsing error response:", e);
      }
      throw new Error(errorMessage);
    }

    const responseData = await response.json();
    console.log("Registration successful:", responseData);

    // Store tokens if provided by backend
    if (responseData.access_token) {
      localStorage.setItem("access_token", responseData.access_token);
    }
    if (responseData.refresh_token) {
      localStorage.setItem("refresh_token", responseData.refresh_token);
    }

    success("Account created successfully! Welcome to our platform!");

    // Redirect to dashboard after a short delay
    setTimeout(() => {
      window.location.href = "/dashboard";
    }, 1500);
  } catch (err) {
    console.error("Registration error:", err);

    let errorMessage = "Registration failed. Please try again.";

    // Handle specific Firebase errors
    if (err.code) {
      errorMessage = getFirebaseErrorMessage(err);
    } else if (err.message) {
      errorMessage = err.message;
    }

    showError(errorMessage);
    error.value = errorMessage;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Custom styles if needed */
</style>
