<!-- FormSection.vue -->
<template name="FormSection">
  <div class="bg-white border border-gray-200 rounded-lg p-6">
    <div class="mb-6">
      <h2 class="text-lg font-semibold text-gray-900">{{ title }}</h2>
      <p v-if="description" class="text-sm text-gray-600 mt-1">{{ description }}</p>
    </div>
    <slot />
  </div>
</template>

<script setup name="FormSection">
defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: null,
  },
});
</script>
