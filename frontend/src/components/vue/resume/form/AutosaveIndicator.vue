<template>
  <div class="flex items-center space-x-2 text-sm">
    <!-- Status Icon -->
    <div class="flex items-center">
      <!-- Saving State -->
      <div v-if="status === 'saving'" class="flex items-center text-blue-600">
        <i class="pi pi-spin pi-spinner mr-1"></i>
        <span>Saving...</span>
      </div>

      <!-- Saved State -->
      <div v-else-if="status === 'saved'" class="flex items-center text-green-600">
        <i class="pi pi-check-circle mr-1"></i>
        <span>{{ lastSavedText || "Saved" }}</span>
      </div>

      <!-- Pending Changes -->
      <div v-else-if="status === 'pending'" class="flex items-center text-amber-600">
        <i class="pi pi-clock mr-1"></i>
        <span>Unsaved changes</span>
      </div>

      <!-- Error State -->
      <div v-else-if="status === 'error'" class="flex items-center text-red-600">
        <i class="pi pi-exclamation-triangle mr-1"></i>
        <span>Save failed</span>
        <button @click="$emit('retry')" class="ml-2 text-xs underline hover:no-underline">
          Retry
        </button>
      </div>

      <!-- Idle State -->
      <div v-else class="flex items-center text-gray-400">
        <i class="pi pi-file mr-1"></i>
        <span>Draft</span>
      </div>
    </div>

    <!-- Manual Save Button (optional) -->
    <button
      v-if="showSaveButton && (status === 'pending' || status === 'error')"
      @click="$emit('save')"
      :disabled="status === 'saving'"
      class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors disabled:opacity-50"
    >
      Save Now
    </button>

    <!-- Settings Button (optional) -->
    <button
      v-if="showSettings"
      @click="toggleSettings"
      class="text-gray-400 hover:text-gray-600 transition-colors"
      title="Autosave Settings"
    >
      <i class="pi pi-cog"></i>
    </button>
  </div>

  <!-- Settings Panel -->
  <div
    v-if="showSettingsPanel"
    class="absolute top-8 right-0 bg-white border border-gray-200 rounded-lg shadow-lg p-4 w-64 z-50"
  >
    <h3 class="font-medium text-gray-900 mb-3">Autosave Settings</h3>

    <div class="space-y-3">
      <!-- Enable/Disable Autosave -->
      <label class="flex items-center">
        <input
          type="checkbox"
          :checked="config.enabled"
          @change="$emit('update-config', { enabled: $event.target.checked })"
          class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <span class="ml-2 text-sm text-gray-700">Enable autosave</span>
      </label>

      <!-- Save Interval -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Save every (seconds)
        </label>
        <select
          :value="config.interval / 1000"
          @change="$emit('update-config', { interval: $event.target.value * 1000 })"
          class="w-full rounded border-gray-300 text-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option :value="1">1 second</option>
          <option :value="3">3 seconds</option>
          <option :value="5">5 seconds</option>
          <option :value="10">10 seconds</option>
          <option :value="30">30 seconds</option>
        </select>
      </div>

      <!-- Show Notifications -->
      <label class="flex items-center">
        <input
          type="checkbox"
          :checked="config.showNotifications"
          @change="$emit('update-config', { showNotifications: $event.target.checked })"
          class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <span class="ml-2 text-sm text-gray-700">Show save notifications</span>
      </label>
    </div>

    <div class="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-500">
      <p>Last saved: {{ lastSavedText || "Never" }}</p>
      <p>Storage used: {{ storageSize }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
// Using PrimeIcons - no imports needed, just CSS classes

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) => ["idle", "saving", "saved", "pending", "error"].includes(value),
  },
  lastSavedText: {
    type: String,
    default: null,
  },
  config: {
    type: Object,
    required: true,
  },
  showSaveButton: {
    type: Boolean,
    default: true,
  },
  showSettings: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["save", "retry", "update-config"]);

const showSettingsPanel = ref(false);

const toggleSettings = () => {
  showSettingsPanel.value = !showSettingsPanel.value;
};

const storageSize = computed(() => {
  if (typeof window === "undefined") return "0 KB";

  try {
    const data = localStorage.getItem("resumeFormData");
    if (!data) return "0 KB";

    const bytes = new Blob([data]).size;
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  } catch {
    return "Unknown";
  }
});

// Close settings panel when clicking outside
const handleClickOutside = (event) => {
  if (showSettingsPanel.value && !event.target.closest(".autosave-settings")) {
    showSettingsPanel.value = false;
  }
};

if (typeof window !== "undefined") {
  document.addEventListener("click", handleClickOutside);
}
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
