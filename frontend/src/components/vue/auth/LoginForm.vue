<template>
  <form @submit.prevent="handleLogin" class="mt-8 space-y-6">
    <BaseInput
      v-model="email"
      label="Email address"
      type="email"
      id="email-address"
      autocomplete="email"
      required
    />
    <BaseInput
      v-model="password"
      label="Password"
      type="password"
      id="password"
      autocomplete="current-password"
      required
    />

    <div class="flex items-center justify-between">
      <label class="flex items-center text-sm text-gray-900">
        <input
          type="checkbox"
          v-model="rememberMe"
          class="h-4 w-4 text-primary-600 border-gray-300 rounded mr-2"
        />
        Remember me
      </label>
      <a href="#" class="text-sm font-medium text-primary-600 hover:text-primary-500"
        >Forgot your password?</a
      >
    </div>

    <BaseButton type="submit" label="Sign in" :loading="loading" full />
    <p v-if="error" class="text-sm text-red-500 mt-2">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { authClient } from "@/lib/AuthClient";
import { useFirebase } from "@/composables/useFirebase";
import { getFirebaseErrorMessage } from "@/utils/getFirebaseErrorMessage";
import { useToast } from "@/composables/useToast";

import BaseInput from "@/components/vue/ui/BaseInput.vue";
import BaseButton from "@/components/vue/ui/BaseButton.vue";

const email = ref("");
const password = ref("");
const rememberMe = ref(false);
const error = ref(null);
const loading = ref(false);

const { success, error: showError, info } = useToast();

const { initAuth } = useFirebase();

const handleLogin = async () => {
  error.value = null;
  loading.value = true;

  try {
    // Ensure Firebase is initialized
    await initAuth();

    console.log("Attempting login...");
    const result = await authClient.login(email.value, password.value, rememberMe.value);

    if (result.status === "2fa_required") {
      info("2FA required. Redirecting...");
      setTimeout(() => {
        window.location.href = "/2fa";
      }, 1000);
    } else {
      success("Login successful!");
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 1000);
    }
  } catch (err) {
    console.error("Login error:", err);
    const message = getFirebaseErrorMessage(err);
    showError(message);
    error.value = message;
  } finally {
    loading.value = false;
  }
};
</script>
