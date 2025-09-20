<template>
  <div class="bg-white p-6 rounded-lg border border-gray-200">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Include Sections</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <label class="flex items-center">
        <input
          type="checkbox"
          v-model="modelValue.includeProjects"
          class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <span class="ml-2 text-sm text-gray-700">Include Projects</span>
      </label>
      <label class="flex items-center">
        <input
          type="checkbox"
          v-model="modelValue.includeCertifications"
          class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <span class="ml-2 text-sm text-gray-700">Include Certifications</span>
      </label>
      <label class="flex items-center">
        <input
          type="checkbox"
          v-model="modelValue.includeLanguages"
          class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <span class="ml-2 text-sm text-gray-700">Include Languages</span>
      </label>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
});
</script>
