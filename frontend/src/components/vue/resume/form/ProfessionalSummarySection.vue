<template>
  <div class="bg-white p-6 rounded-lg border border-gray-200">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Professional Summary</h3>
    <div>
      <label for="summary" class="block text-sm font-medium text-gray-700 mb-2">
        Professional Summary (Optional)
      </label>
      <textarea
        id="summary"
        v-model="modelValue.summary"
        rows="4"
        placeholder="Brief overview of your professional background, key skills, and career objectives. Leave blank to auto-generate based on your experience."
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      ></textarea>
      <p class="text-xs text-gray-500 mt-1">
        If left blank, we'll generate a professional summary based on your experience and
        skills.
      </p>
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
