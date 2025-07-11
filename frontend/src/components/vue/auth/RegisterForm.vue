<template>
  <form @submit.prevent="handleRegister" class="space-y-6">
    <BaseInput v-model="email" type="email" label="Email" id="register-email" required />
    <BaseInput
      v-model="password"
      type="password"
      label="Password"
      id="register-password"
      required
    />
    <BaseInput
      v-model="displayName"
      type="text"
      label="Display Name"
      id="display-name"
      required
    />

    <BaseButton type="submit" label="Create Account" :loading="loading" full />
    <p v-if="error" class="text-sm text-red-500 mt-2">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { createUserWithEmailAndPassword, updateProfile } from "firebase/auth";
import { getFirebaseErrorMessage } from "@/utils/getFirebaseErrorMessage";
import { useFirebase } from "@/composables/useFirebase";
import { authClient } from "@/lib/AuthClient";

import BaseInput from "@/components/vue/ui/BaseInput.vue";
import BaseButton from "@/components/vue/ui/BaseButton.vue";

import Toast from "vue-toast-notification";

const toast = Toast.useToast();

const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const displayName = ref("");
const agreed = ref(false);
const loading = ref(false);
const error = ref(null);

const { initAuth, getFirebaseAuth } = useFirebase();

const handleRegister = async () => {
  error.value = null;

  if (password.value !== confirmPassword.value) {
    toast.error("Passwords do not match");
    return;
  }

  loading.value = true;
  try {
    await initAuth();
    const auth = await getFirebaseAuth();
    const userCredential = await createUserWithEmailAndPassword(
      auth,
      email.value,
      password.value
    );

    await updateProfile(userCredential.user, {
      displayName: displayName.value,
    });

    const idToken = await userCredential.user.getIdToken();

    await authClient.loginWith2FA(idToken, "", false);

    toast.success("Account created successfully!");
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
