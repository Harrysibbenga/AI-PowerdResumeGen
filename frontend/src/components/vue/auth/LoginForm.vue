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

import BaseInput from "@/components/vue/ui/BaseInput.vue";
import BaseButton from "@/components/vue/ui/BaseButton.vue";

import Toast from "vue-toast-notification";

const email = ref("");
const password = ref("");
const rememberMe = ref(false);
const error = ref(null);
const loading = ref(false);
const toast = Toast.useToast();

const { initAuth } = useFirebase();

const handleLogin = async () => {
  error.value = null;
  loading.value = true;

  try {
    await initAuth();
    const result = await authClient.login(email.value, password.value, rememberMe.value);

    if (result.status === "2fa_required") {
      toast.info("2FA required. Redirecting...");
      window.location.href = "/2fa";
    } else {
      toast.success("Login successful!");
      window.location.href = "/dashboard";
    }
  } catch (err) {
    const message = getFirebaseErrorMessage(err);
    toast.error(message);
    error.value = message;
  } finally {
    loading.value = false;
  }
};
</script>
