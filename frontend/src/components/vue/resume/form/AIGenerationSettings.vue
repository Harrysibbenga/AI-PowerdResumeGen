<template>
  <div class="bg-white p-6 rounded-lg border border-gray-200">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Resume Settings</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label for="tone" class="block text-sm font-medium text-gray-700 mb-2">
          Tone
        </label>
        <select
          id="tone"
          v-model="modelValue.tone"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="professional">Professional</option>
          <option value="creative">Creative</option>
          <option value="formal">Formal</option>
          <option value="casual">Casual</option>
        </select>
      </div>
      <div>
        <label for="length" class="block text-sm font-medium text-gray-700 mb-2">
          Length
        </label>
        <select
          id="length"
          v-model="modelValue.length"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="short">Short (1 page)</option>
          <option value="standard">Standard (1-2 pages)</option>
          <option value="detailed">Detailed (2+ pages)</option>
        </select>
      </div>
      <div>
        <label for="template" class="block text-sm font-medium text-gray-700 mb-2">
          Template
        </label>
        <select
          id="template"
          v-model="modelValue.templateId"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="modern">Modern</option>
          <option value="classic">Classic</option>
          <option value="creative">Creative</option>
          <option value="minimal">Minimal</option>
          <option value="executive">Executive</option>
        </select>
      </div>
    </div>
    <div class="mt-4">
      <label for="focusKeywords" class="block text-sm font-medium text-gray-700 mb-2">
        Focus Keywords (Optional)
      </label>
      <input
        id="focusKeywords"
        v-model="modelValue.focusKeywords"
        type="text"
        placeholder="e.g., machine learning, cloud computing, agile"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      />
      <p class="text-xs text-gray-500 mt-1">
        Keywords to emphasize throughout the resume (comma-separated)
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
