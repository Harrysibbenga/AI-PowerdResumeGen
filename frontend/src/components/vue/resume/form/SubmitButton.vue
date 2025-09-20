<!-- SubmitButton.vue -->
<template name="SubmitButton">
  <button
    type="submit"
    :disabled="disabled || loading"
    :class="buttonClasses"
    class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-200"
  >
    <!-- Loading Spinner -->
    <i v-if="loading" class="pi pi-spin pi-spinner mr-3 text-white"></i>

    <!-- Success Icon (when not loading and not disabled) -->
    <i v-else-if="!disabled" class="pi pi-check mr-2"></i>

    <!-- Button Text -->
    <span>{{ buttonText }}</span>
  </button>
</template>

<script setup name="SubmitButton">
import { computed } from "vue";
// No icon imports needed with PrimeIcons

const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  isEditMode: {
    type: Boolean,
    default: false,
  },
});

const buttonText = computed(() => {
  if (props.loading) {
    return props.isEditMode ? "Updating Resume..." : "Generating Resume...";
  }
  return props.isEditMode ? "Update Resume" : "Generate Resume";
});

const buttonClasses = computed(() => {
  if (props.disabled || props.loading) {
    return "bg-gray-300 text-gray-500 cursor-not-allowed";
  }
  return "bg-primary-600 hover:bg-primary-700 text-white focus:ring-primary-500 hover:shadow-lg transform hover:-translate-y-0.5";
});
</script>
