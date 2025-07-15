<template>
  <form @submit.prevent="handleVerify2FA" class="space-y-4">
    <BaseInput
      v-model="code"
      label="Two-Factor Code"
      type="text"
      id="two-factor-code"
      required
      placeholder="Enter 6-digit code"
    />

    <BaseButton type="submit" label="Verify 2FA" :loading="loading" full />

    <p v-if="error" class="text-sm text-red-500 mt-2">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { authClient } from "@/services";
import { useFirebase } from "@/composables/useFirebase";
import { getFirebaseErrorMessage } from "@/utils/getFirebaseErrorMessage";

import BaseInput from "@/components/vue/ui/BaseInput.vue";
import BaseButton from "@/components/vue/ui/BaseButton.vue";

import Toast from "vue-toast-notification";

const code = ref("");
const error = ref(null);
const loading = ref(false);
const toast = Toast.useToast();

const { getCurrentUser } = useFirebase();

const handleVerify2FA = async () => {
  error.value = null;
  loading.value = true;

  try {
    const idToken = await getCurrentUser()?.getIdToken();
    await authClient.loginWith2FA(idToken, code.value, true);

    toast.success("2FA verified! Logging you in...");
    window.location.href = "/dashboard";
  } catch (err) {
    const message = getFirebaseErrorMessage(err);
    toast.error(message);
    error.value = message;
  } finally {
    loading.value = false;
  }
};
</script>
