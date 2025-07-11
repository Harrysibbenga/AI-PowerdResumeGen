<template>
  <div v-if="authInitialized">
    <div v-if="isAuthenticated" class="min-h-[calc(100vh-300px)] py-12 px-4">
      <div class="container mx-auto max-w-7xl">
        <h1 class="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        <ResumeContainer />

        <AccountSettings
          :user="user"
          @update-success="handleSuccess"
          @update-error="handleError"
        />
      </div>
    </div>
    <div v-else class="text-center text-gray-500 py-20">Redirecting to login...</div>
  </div>
</template>

<script setup>
import { useFirebase } from "@/composables/useFirebase";
import Toast from "vue-toast-notification";
import ResumeContainer from "@/components/vue/dashboard/resume/ResumeContainer.vue";
import AccountSettings from "@/components/vue/dashboard/AccountSettings.vue";

const toast = Toast.useToast();
const { initAuth, user, isAuthenticated, authInitialized } = useFirebase();

await initAuth();

const handleSuccess = (msg) => toast.success(msg);
const handleError = (msg) => toast.error(msg);
</script>
