<template>
  <div class="space-y-1">
    <label :for="id" class="sr-only">{{ label }}</label>
    <input
      :id="id"
      :type="type"
      :autocomplete="autocomplete"
      :placeholder="label"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      class="block w-full px-3 py-2 border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-md sm:text-sm"
      :required="required"
    />
  </div>
</template>

<script setup>
defineProps({
  modelValue: String,
  label: String,
  type: { type: String, default: "text" },
  id: String,
  autocomplete: String,
  required: Boolean,
});

defineEmits(["update:modelValue"]);
</script>
