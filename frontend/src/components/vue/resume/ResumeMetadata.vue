<template>
  <div
    v-if="metadata"
    class="mt-3 flex items-center space-x-6 text-sm text-gray-500"
  >
    <div class="text-sm text-gray-500">
      <span>Title: </span>
      <span class="font-medium text-gray-700">{{ metadata.title }}</span>
    </div>
    <span v-if="metadata.target_job_title" class="flex items-center">
      <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
        <path
          fill-rule="evenodd"
          d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z"
          clip-rule="evenodd"
        ></path>
      </svg>
      {{ metadata.target_job_title }}
      <span v-if="metadata.target_job_role" class="ml-1"
        >({{ metadata.target_job_role }})</span
      >
    </span>
    <span v-if="metadata.industry" class="flex items-center">
      <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
        <path
          fill-rule="evenodd"
          d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
          clip-rule="evenodd"
        ></path>
      </svg>
      {{ formatIndustry(metadata.industry) }}
    </span>
    <span v-if="metadata.template_id" class="flex items-center">
      <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
        <path
          fill-rule="evenodd"
          d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
          clip-rule="evenodd"
        ></path>
      </svg>
      {{ formatTemplate(metadata.template_id) }} Template
    </span>
    <span v-if="metadata.word_count" class="flex items-center">
      <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
        <path
          fill-rule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
          clip-rule="evenodd"
        ></path>
      </svg>
      {{ metadata.word_count?.toLocaleString() }} words
    </span>
  </div>
</template>

<script setup>
const props = defineProps({
  metadata: {
    type: Object,
    default: null,
  }
});

const formatIndustry = (industry) => {
  return industry?.charAt(0).toUpperCase() + industry?.slice(1).replace("_", " ") || "";
};

const formatTemplate = (template) => {
  return template?.charAt(0).toUpperCase() + template?.slice(1) || "";
};
</script>