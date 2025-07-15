<template>
  <div class="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-md">
    <div>
      <div
        class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100 mb-6"
      >
        <svg
          class="h-6 w-6 text-primary-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-3.586l6.293-6.293A6 6 0 0121 9z"
          />
        </svg>
      </div>
      <h1 class="text-center text-3xl font-extrabold text-gray-900">
        Forgot your password?
      </h1>
      <p class="mt-2 text-center text-sm text-gray-600">
        No worries! Enter your email address and we'll send you a link to reset your
        password.
      </p>
      <p class="mt-2 text-center text-sm text-gray-600">
        Or
        <a href="/login" class="font-medium text-primary-600 hover:text-primary-500">
          back to sign in
        </a>
      </p>
    </div>

    <ForgotPasswordForm />

    <!-- Additional Help Section -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
            <path
              fill-rule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-blue-800">Need help?</h3>
          <div class="mt-2 text-sm text-blue-700">
            <p>
              If you don't receive an email within a few minutes, check your spam folder
              or
              <a href="/contact" class="font-medium underline">contact support</a>.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Security Notice -->
    <div class="text-center">
      <p class="text-xs text-gray-500">
        For security reasons, we won't tell you whether this email address is in our
        system.
      </p>
    </div>
  </div>
</template>

<script setup>
import ForgotPasswordForm from "@/components/vue/auth/ForgotPasswordForm.vue";
</script>
