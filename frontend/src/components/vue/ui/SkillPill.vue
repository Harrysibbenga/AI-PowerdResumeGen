<template>
  <span
    :class="pillClasses"
    class="inline-block px-3 py-1.5 rounded-full text-sm font-medium transition-colors"
  >
    {{ label }}
    <span v-if="sublabel" class="ml-1 font-normal opacity-90">({{ sublabel }})</span>
  </span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  sublabel: {
    type: String,
    default: null,
  },
  variant: {
    type: String,
    default: "primary",
    validator: (value) => ["primary", "green", "blue", "purple", "gray"].includes(value),
  },
  size: {
    type: String,
    default: "md",
    validator: (value) => ["sm", "md", "lg"].includes(value),
  },
});

const pillClasses = computed(() => {
  const variants = {
    primary: "bg-primary-100 text-primary-800 hover:bg-primary-200",
    green: "bg-green-100 text-green-800 hover:bg-green-200",
    blue: "bg-blue-100 text-blue-800 hover:bg-blue-200",
    purple: "bg-purple-100 text-purple-800 hover:bg-purple-200",
    gray: "bg-gray-100 text-gray-800 hover:bg-gray-200",
  };

  const sizes = {
    sm: "px-2 py-1 text-xs",
    md: "px-3 py-1.5 text-sm",
    lg: "px-4 py-2 text-base",
  };

  return `${variants[props.variant]} ${sizes[props.size]}`;
});
</script>
