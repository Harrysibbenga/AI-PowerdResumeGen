<template>
  <div class="bg-white p-6 rounded-lg border border-gray-200">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">Languages</h3>
      <button
        v-if="!showLanguageForm"
        type="button"
        @click="startAddingLanguage"
        class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        + Add Language
      </button>
    </div>

    <!-- Display existing languages -->
    <div v-if="languages.length > 0" class="space-y-4 mb-6">
      <div class="text-sm font-medium text-gray-700">Your Languages:</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="(languageEntry, index) in languages"
          :key="index"
          class="bg-gray-50 p-4 border border-gray-200 rounded-lg"
        >
          <div class="flex justify-between items-start mb-2">
            <h4 class="font-medium text-gray-900">
              {{ languageEntry.language || languageEntry.name || `Language #${index + 1}` }}
            </h4>
            <button
              type="button"
              @click="removeLanguage(index)"
              class="text-red-600 hover:text-red-800 text-sm font-medium"
            >
              Remove
            </button>
          </div>
          <div class="flex items-center gap-2">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {{ languageEntry.proficiency || 'Not specified' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Language addition interface -->
    <div v-if="showLanguageForm" class="bg-white p-6 border border-gray-200 rounded-lg shadow-sm space-y-6">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-medium text-gray-900">Add New Language</h3>
        <button
          type="button"
          @click="cancelAddLanguage"
          class="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>

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
      <div class="flex justify-end space-x-3 pt-4 border-t">
        <button
          type="button"
          @click="cancelAddLanguage"
          class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="addLanguage"
          :disabled="!newLanguage.language || !newLanguage.proficiency"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Add Language
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="languages.length === 0 && !showLanguageForm" class="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
      <div class="text-4xl mb-2">🌍</div>
      <p class="text-gray-600 font-medium">No languages added yet</p>
      <p class="text-gray-500 text-sm mt-1">Click "Add Language" to showcase your language skills</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import defaultLanguagesData from "@/data/defaultLanguages.json";

const props = defineProps({
  modelValue: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(['update:modelValue', 'change']);

// Debug logging
onMounted(() => {
  console.log('LanguagesInput mounted with modelValue:', props.modelValue);
  console.log('Languages array type:', typeof props.modelValue, 'isArray:', Array.isArray(props.modelValue));
  if (Array.isArray(props.modelValue)) {
    console.log('Languages count:', props.modelValue.length);
    props.modelValue.forEach((language, index) => {
      console.log(`Language ${index}:`, language.language || language.name || 'Unnamed');
    });
  }
});

// Safe access to languages array
const languages = computed(() => {
  console.log('LanguagesInput - modelValue:', props.modelValue);
  if (!Array.isArray(props.modelValue)) {
    console.warn('LanguagesInput - modelValue is not an array:', typeof props.modelValue, props.modelValue);
    return [];
  }
  return props.modelValue;
});

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

// Update languages array
const updateLanguages = (newLanguages) => {
  console.log('LanguagesInput - updating languages:', newLanguages);
  emit('update:modelValue', newLanguages);
  emit('change');
};

// Initialize languages array if it doesn't exist
const initializeLanguages = () => {
  if (!Array.isArray(languages.value)) {
    updateLanguages([]);
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
    const exists = languages.value.some(
      (lang) => (lang.language || lang.name || '').toLowerCase() === newLanguage.language.toLowerCase()
    );

    if (exists) {
      alert("This language is already added");
      return;
    }

    const updatedLanguages = [...languages.value, {
      language: newLanguage.language,
      name: newLanguage.language, // Support both formats
      proficiency: newLanguage.proficiency,
    }];

    updateLanguages(updatedLanguages);
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
  const updatedLanguages = [...languages.value];
  updatedLanguages.splice(index, 1);
  updateLanguages(updatedLanguages);
};
</script>
