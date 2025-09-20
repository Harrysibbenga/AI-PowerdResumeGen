<template>
  <h2 class="text-2xl font-bold text-gray-900 mb-4 pb-2 border-b-2 border-primary-500">
    <slot>{{ title }}</slot>
  </h2>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: '',
  }
});
</script>