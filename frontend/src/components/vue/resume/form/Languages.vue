<template>
  <div class="bg-gray-50 p-6 rounded-md">
    <h2 class="text-xl font-semibold mb-4">Languages</h2>

    <!-- Display existing languages with edit capability -->
    <div v-if="form.languages && form.languages.length > 0" class="space-y-3 mb-4">
      <div class="text-sm text-gray-600 mb-2">Your languages:</div>
      <div
        v-for="(languageEntry, index) in form.languages"
        :key="index"
        class="flex items-center justify-between bg-white p-3 rounded-md border"
      >
        <div class="flex items-center space-x-3">
          <span class="font-medium">{{ languageEntry.language }}</span>
          <span class="text-sm px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
            {{ languageEntry.proficiency }}
          </span>
        </div>
        <button
          type="button"
          @click="removeLanguage(index)"
          class="text-red-600 hover:text-red-800 text-sm"
        >
          Remove
        </button>
      </div>
    </div>

    <!-- Language addition interface -->
    <div v-if="showLanguageForm" class="bg-white p-4 rounded-md border space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Language Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Select Language
          </label>
          <div class="relative">
            <select
              v-model="newLanguage.language"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="onLanguageSelect"
            >
              <option value="">Choose a language...</option>
              <option
                v-for="lang in availableLanguages"
                :key="lang.name"
                :value="lang.name"
              >
                {{ lang.name }}
              </option>
              <option value="custom">+ Add custom language</option>
            </select>
          </div>

          <!-- Custom language input -->
          <div v-if="showCustomLanguage" class="mt-2">
            <input
              v-model="customLanguageName"
              type="text"
              placeholder="Enter language name"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="newLanguage.language = customLanguageName"
            />
          </div>
        </div>

        <!-- Proficiency Level Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Proficiency Level
          </label>
          <select
            v-model="newLanguage.proficiency"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :disabled="!newLanguage.language"
          >
            <option value="">Select level...</option>
            <option
              v-for="level in proficiencyLevels"
              :key="level.value"
              :value="level.value"
            >
              {{ level.label }} - {{ level.description }}
            </option>
          </select>
        </div>
      </div>

      <!-- Preview -->
      <div
        v-if="newLanguage.language && newLanguage.proficiency"
        class="p-3 bg-gray-50 rounded-md"
      >
        <div class="text-sm text-gray-600">Preview:</div>
        <div class="flex items-center space-x-3 mt-1">
          <span class="font-medium">{{ newLanguage.language }}</span>
          <span class="text-sm px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
            {{ newLanguage.proficiency }}
          </span>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="flex space-x-2">
        <button
          type="button"
          @click="addLanguage"
          :disabled="!newLanguage.language || !newLanguage.proficiency"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Add Language
        </button>
        <button
          type="button"
          @click="cancelAddLanguage"
          class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </div>

    <!-- Add Language button -->
    <button
      v-if="!showLanguageForm"
      type="button"
      @click="startAddingLanguage"
      class="px-4 py-2 text-blue-600 hover:text-blue-800 border border-blue-300 rounded-md hover:bg-blue-50"
    >
      + Add Language
    </button>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from "vue";
import defaultLanguagesData from "@/data/defaultLanguages.json";

defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
});

const form = defineModel("modelValue");

// Extract proficiency levels from the JSON file
const proficiencyLevels = computed(() => {
  if (defaultLanguagesData.proficiencyLevels) {
    return defaultLanguagesData.proficiencyLevels;
  }
  // Fallback if not in JSON file
  return [
    { value: "Native", label: "Native", description: "Native or bilingual proficiency" },
    { value: "Fluent", label: "Fluent", description: "Full professional proficiency" },
    {
      value: "Advanced",
      label: "Advanced",
      description: "Professional working proficiency",
    },
    {
      value: "Intermediate",
      label: "Intermediate",
      description: "Limited working proficiency",
    },
    { value: "Beginner", label: "Beginner", description: "Elementary proficiency" },
  ];
});

// Extract languages from the JSON file
const availableLanguages = computed(() => {
  if (defaultLanguagesData.languages) {
    return defaultLanguagesData.languages;
  }
  // Fallback if structure is different
  return defaultLanguagesData;
});

// State
const showLanguageForm = ref(false);
const showCustomLanguage = ref(false);
const customLanguageName = ref("");
const newLanguage = reactive({
  language: "",
  proficiency: "",
});

// Initialize languages array if it doesn't exist
const initializeLanguages = () => {
  if (!form.value.languages) {
    form.value.languages = [];
  }
};

// Start adding a new language
const startAddingLanguage = () => {
  initializeLanguages();
  showLanguageForm.value = true;
  resetNewLanguage();
};

// Handle language selection
const onLanguageSelect = () => {
  if (newLanguage.language === "custom") {
    showCustomLanguage.value = true;
    newLanguage.language = "";
  } else {
    showCustomLanguage.value = false;
    customLanguageName.value = "";
  }
};

// Add the new language to the form
const addLanguage = () => {
  if (newLanguage.language && newLanguage.proficiency) {
    // Check if language already exists
    const exists = form.value.languages.some(
      (lang) => lang.language.toLowerCase() === newLanguage.language.toLowerCase()
    );

    if (exists) {
      alert("This language is already added");
      return;
    }

    form.value.languages.push({
      language: newLanguage.language,
      proficiency: newLanguage.proficiency,
    });

    resetNewLanguage();
    showLanguageForm.value = false;
  }
};

// Cancel adding language
const cancelAddLanguage = () => {
  resetNewLanguage();
  showLanguageForm.value = false;
};

// Reset the new language form
const resetNewLanguage = () => {
  newLanguage.language = "";
  newLanguage.proficiency = "";
  showCustomLanguage.value = false;
  customLanguageName.value = "";
};

// Remove a language
const removeLanguage = (index) => {
  form.value.languages.splice(index, 1);
};
</script>
