<template>
  <div>
    <!-- Loading State -->
    <div v-if="!authInitialized" class="flex items-center gap-4">
      <div class="animate-pulse flex items-center gap-2">
        <div class="w-8 h-8 bg-gray-200 rounded-full"></div>
        <div class="w-20 h-4 bg-gray-200 rounded"></div>
      </div>
    </div>

    <!-- Authenticated State -->
    <div v-else-if="isAuthenticated" class="flex items-center gap-4">
      <UserMenu :user="user" />
    </div>

    <!-- Unauthenticated State -->
    <div v-else class="flex items-center gap-3">
      <a
        href="/login"
        class="text-gray-700 hover:text-primary-600 transition-colors duration-200"
      >
        Log In
      </a>
      <a
        href="/register"
        class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors duration-200"
      >
        Sign Up
      </a>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import UserMenu from "@/components/vue/common/UserMenu.vue";

// No props needed - handle all auth logic internally
const { user, isAuthenticated, authInitialized, initAuth } = useFirebase();

onMounted(async () => {
  try {
    await initAuth();
  } catch (error) {
    console.error("Failed to initialize auth in navigation:", error);
  }
});
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
