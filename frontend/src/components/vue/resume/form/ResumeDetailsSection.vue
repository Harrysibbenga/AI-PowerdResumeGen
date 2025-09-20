<template>
  <div class="bg-white p-6 rounded-lg border border-gray-200">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Resume Details</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="md:col-span-2">
        <label for="resumeTitle" class="block text-sm font-medium text-gray-700 mb-2">
          Resume Title *
        </label>
        <input
          id="resumeTitle"
          v-model="title"
          type="text"
          placeholder="e.g., Senior Software Engineer Resume"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          required
        />
      </div>

      <div>
        <label for="targetJobTitle" class="block text-sm font-medium text-gray-700 mb-2">
          Target Job Title *
        </label>
        <input
          id="targetJobTitle"
          v-model="targetJobTitle"
          type="text"
          placeholder="e.g., Senior Software Engineer"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          required
        />
      </div>

      <div>
        <label for="targetJobRole" class="block text-sm font-medium text-gray-700 mb-2">
          Target Job Role/Level
        </label>
        <select
          id="targetJobRole"
          v-model="targetJobRole"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="">Select level (optional)</option>
          <option value="Entry Level">Entry Level</option>
          <option value="Junior">Junior</option>
          <option value="Mid-Level">Mid-Level</option>
          <option value="Senior">Senior</option>
          <option value="Lead">Lead</option>
          <option value="Principal">Principal</option>
          <option value="Manager">Manager</option>
          <option value="Senior Manager">Senior Manager</option>
          <option value="Director">Director</option>
          <option value="VP">VP</option>
          <option value="C-Level">C-Level</option>
        </select>
      </div>

      <div class="md:col-span-2">
        <label for="targetCompany" class="block text-sm font-medium text-gray-700 mb-2">
          Target Company (Optional)
        </label>
        <input
          id="targetCompany"
          v-model="targetCompany"
          type="text"
          placeholder="e.g., Google, Microsoft, or leave blank for general use"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
        <p class="text-xs text-gray-500 mt-1">
          Optionally specify a target company to tailor the resume content
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['update:modelValue', 'change']);

// Safe access to model values with defaults
const safeModelValue = computed(() => props.modelValue || {
  title: '',
  targetJobTitle: '',
  targetJobRole: '',
  targetCompany: ''
});

// Create reactive computed properties for each field
const title = computed({
  get: () => safeModelValue.value.title || '',
  set: (value) => {
    console.log('ResumeDetailsSection: title changed to:', value);
    if (props.modelValue) {
      const updated = { ...props.modelValue, title: value };
      emit('update:modelValue', updated);
      emit('change');
    }
  }
});

const targetJobTitle = computed({
  get: () => safeModelValue.value.targetJobTitle || '',
  set: (value) => {
    console.log('ResumeDetailsSection: targetJobTitle changed to:', value);
    if (props.modelValue) {
      const updated = { ...props.modelValue, targetJobTitle: value };
      emit('update:modelValue', updated);
      emit('change');
    }
  }
});

const targetJobRole = computed({
  get: () => safeModelValue.value.targetJobRole || '',
  set: (value) => {
    console.log('ResumeDetailsSection: targetJobRole changed to:', value);
    if (props.modelValue) {
      const updated = { ...props.modelValue, targetJobRole: value };
      emit('update:modelValue', updated);
      emit('change');
    }
  }
});

const targetCompany = computed({
  get: () => safeModelValue.value.targetCompany || '',
  set: (value) => {
    console.log('ResumeDetailsSection: targetCompany changed to:', value);
    if (props.modelValue) {
      const updated = { ...props.modelValue, targetCompany: value };
      emit('update:modelValue', updated);
      emit('change');
    }
  }
});

// Debug logging
console.log('ResumeDetailsSection mounted with modelValue:', props.modelValue);
</script>
