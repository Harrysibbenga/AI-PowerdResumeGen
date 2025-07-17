<template>
  <div class="bg-gray-50 p-6 rounded-md">
    <h2 class="text-xl font-semibold mb-4">Languages</h2>
    <div class="space-y-2">
      <div
        v-for="(language, index) in form.languages"
        :key="index"
        class="flex items-center"
      >
        <input
          v-model="form.languages[index]"
          type="text"
          placeholder="e.g., Spanish (Fluent), French (Intermediate)"
          class="flex-1 px-3 py-2 border border-gray-300 rounded-md"
        />
        <button
          type="button"
          @click="removeLanguage(index)"
          class="ml-2 text-red-600 hover:text-red-800"
        >
          Remove
        </button>
      </div>
    </div>
    <button
      type="button"
      @click="form.languages.push('')"
      class="mt-2 text-blue-600 hover:text-blue-800"
    >
      + Add Language
    </button>
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
