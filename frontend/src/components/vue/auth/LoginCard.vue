<template>
  <div class="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-md">
    <div>
      <h1 class="text-center text-3xl font-extrabold text-gray-900">
        Sign in to your account
      </h1>
      <p class="mt-2 text-center text-sm text-gray-600">
        Or
        <a href="/register" class="font-medium text-primary-600 hover:text-primary-500">
          create a new account
        </a>
      </p>
    </div>

    <LoginForm />
  </div>
</template>

<script setup>
import LoginForm from "@/components/vue/auth/LoginForm.vue";
</script>
