<template>
  <div>
    <div v-if="isLoading" class="text-center py-8">Loading...</div>

    <div v-else-if="isAuthenticated">
      <ResumeForm />
    </div>

    <div v-else class="py-12 text-center">
      <div class="max-w-md mx-auto bg-white rounded-lg p-8">
        <h2 class="text-2xl font-bold mb-4">Login Required</h2>
        <p class="text-gray-600 mb-6">Please log in to create and save your resume.</p>
        <div class="flex justify-center gap-4">
          <a href="/login" class="px-4 py-2 bg-blue-600 text-white rounded"> Log In </a>
          <a
            href="/register"
            class="px-4 py-2 border border-blue-600 text-blue-600 rounded"
          >
            Register
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ResumeForm from "@/components/vue/resume/form/ResumeForm.vue";
import { useFirebase } from "@/composables/useFirebase";

const { user, isLoading, isAuthenticated, initAuth } = useFirebase();

initAuth(); // Start listening on mount
</script>
