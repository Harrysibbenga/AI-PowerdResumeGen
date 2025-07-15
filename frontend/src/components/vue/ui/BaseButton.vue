<template>
  <button
    :type="type"
    :class="[
      'group relative flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white',
      full ? 'w-full' : '',
      loading ? 'bg-gray-400' : 'bg-primary-600 hover:bg-primary-700',
      'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500',
    ]"
    :disabled="loading"
  >
    <span v-if="!loading">{{ label }}</span>
    <span v-else>Loading...</span>
  </button>
</template>

<script setup>
defineProps({
  type: { type: String, default: "button" },
  label: String,
  loading: Boolean,
  full: Boolean,
});
</script>
