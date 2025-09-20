<template>
  <div
    class="bg-white rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow duration-200"
  >
    <!-- Card Header -->
    <div class="p-4 border-b border-gray-100">
      <div class="flex justify-between items-start">
        <div class="flex-1">
          <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ resume.title }}</h3>
          <div class="flex items-center text-sm text-gray-600 mb-2">
            <span class="font-medium">{{ targetJobTitle }}</span>
            <span v-if="targetJobRole" class="mx-2">•</span>
            <span v-if="targetJobRole" class="text-gray-500">{{ targetJobRole }}</span>
          </div>
          <div v-if="targetCompany" class="text-sm text-blue-600 mb-2">
            <span class="inline-flex items-center">
              <i class="pi pi-building w-4 h-4 mr-1"></i>
              Targeting: {{ targetCompany }}
            </span>
          </div>
        </div>

        <!-- Status Badge -->
        <div class="flex flex-col items-end space-y-2">
          <span
            :class="statusBadgeClass"
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
          >
            {{ statusText }}
          </span>
          <span
            :class="templateBadgeClass"
            class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
          >
            {{ formattedTemplate }}
          </span>
        </div>
      </div>
    </div>

    <!-- Card Body -->
    <div class="p-4">
      <!-- Summary Excerpt -->
      <div v-if="summaryExcerpt" class="mb-3">
        <p class="text-sm text-gray-600 leading-relaxed">{{ summaryExcerpt }}</p>
      </div>

      <!-- Industry and Stats -->
      <div class="flex items-center justify-between text-sm text-gray-500 mb-4">
        <div class="flex items-center space-x-4">
          <span class="inline-flex items-center">
            <i class="pi pi-briefcase w-4 h-4 mr-1"></i>
            {{ formattedIndustry }}
          </span>
          <span class="inline-flex items-center">
            <i class="pi pi-list w-4 h-4 mr-1"></i>
            {{ resume.sections_count || "N/A" }} sections
          </span>
          <span v-if="resume.word_count" class="inline-flex items-center">
            <i class="pi pi-info-circle w-4 h-4 mr-1"></i>
            {{ formattedWordCount }} words
          </span>
        </div>
      </div>

      <!-- Timestamps -->
      <div class="text-xs text-gray-400 mb-4">
        <div>Created: {{ formattedCreatedDate }}</div>
        <div v-if="shouldShowUpdatedDate">Updated: {{ formattedUpdatedDate }}</div>
      </div>
    </div>

    <!-- Card Actions -->
    <div class="px-4 py-3 bg-gray-50 border-t border-gray-100 rounded-b-lg">
      <div class="flex items-center justify-between">
        <div class="flex space-x-2">
          <!-- View Button -->
          <button
            @click="viewResume"
            class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
          >
            <i class="pi pi-eye w-4 h-4 mr-1"></i>
            View
          </button>

          <!-- Edit Button -->
          <button
            @click="editResume"
            class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
          >
            <i class="pi pi-pencil w-4 h-4 mr-1"></i>
            Edit
          </button>

          <!-- Duplicate Button -->
          <button
            @click="duplicateResume"
            class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
          >
            <i class="pi pi-copy w-4 h-4 mr-1"></i>
            Copy
          </button>
        </div>

        <!-- Export/Download Button -->
        <div class="flex space-x-2">
          <button
            @click="exportResume"
            :disabled="isExporting"
            :class="exportButtonClass"
            class="inline-flex items-center px-3 py-1.5 border shadow-sm text-xs font-medium rounded focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors disabled:opacity-50"
          >
            <i v-if="!isExporting" class="pi pi-download w-4 h-4 mr-1"></i>
            <i v-else class="pi pi-spin pi-spinner w-4 h-4 mr-1"></i>
            {{ exportButtonText }}
          </button>

          <!-- More Options Menu -->
          <div class="relative" ref="menuContainer">
            <button
              @click="toggleMenu"
              class="inline-flex items-center px-2 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
            >
              <i class="pi pi-ellipsis-v w-4 h-4"></i>
            </button>

            <!-- Dropdown Menu -->
            <Transition
              enter-active-class="transition ease-out duration-100"
              enter-from-class="transform opacity-0 scale-95"
              enter-to-class="transform opacity-100 scale-100"
              leave-active-class="transition ease-in duration-75"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95"
            >
              <div
                v-if="showMenu"
                class="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10"
              >
                <div class="py-1">
                  <button
                    @click="regenerateContent"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    <i class="pi pi-refresh w-4 h-4 inline mr-2"></i>
                    Regenerate Content
                  </button>
                  <button
                    @click="shareResume"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    <i class="pi pi-share-alt w-4 h-4 inline mr-2"></i>
                    Share Resume
                  </button>
                  <button
                    @click="deleteResume"
                    class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <i class="pi pi-trash w-4 h-4 inline mr-2"></i>
                    Delete Resume
                  </button>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

// Props
const props = defineProps({
  resume: {
    type: Object,
    required: true,
  },
});

// Emits
const emit = defineEmits([
  "view",
  "edit",
  "duplicate",
  "export",
  "regenerate",
  "share",
  "delete",
]);

// Reactive state
const isExporting = ref(false);
const showMenu = ref(false);
const menuContainer = ref(null);

// Check if we're in browser environment
const isBrowser = typeof window !== "undefined";

// Computed properties for cleaner template
const targetJobTitle = computed(
  () => props.resume.target_job_title || props.resume.targetJobTitle
);

const targetJobRole = computed(
  () => props.resume.target_job_role || props.resume.targetJobRole
);

const targetCompany = computed(
  () => props.resume.target_company || props.resume.targetCompany
);

const summaryExcerpt = computed(
  () => props.resume.summary_excerpt || props.resume.summary
);

const statusBadgeClass = computed(() => {
  const classes = {
    free: "bg-gray-100 text-gray-800",
    paid: "bg-green-100 text-green-800",
    subscribed: "bg-blue-100 text-blue-800",
  };
  return classes[props.resume.export_status] || "bg-gray-100 text-gray-800";
});

const statusText = computed(() => {
  const texts = {
    free: "Free",
    paid: "Exported",
    subscribed: "Pro",
  };
  return texts[props.resume.export_status] || "Free";
});

const templateBadgeClass = computed(() => {
  const classes = {
    modern: "bg-purple-100 text-purple-800",
    classic: "bg-blue-100 text-blue-800",
    creative: "bg-pink-100 text-pink-800",
    minimal: "bg-gray-100 text-gray-800",
    executive: "bg-indigo-100 text-indigo-800",
  };
  return classes[props.resume.template_id] || "bg-gray-100 text-gray-800";
});

const formattedTemplate = computed(() => {
  if (!props.resume.template_id) return "Default";
  return (
    props.resume.template_id.charAt(0).toUpperCase() + props.resume.template_id.slice(1)
  );
});

const formattedIndustry = computed(() => {
  if (!props.resume.industry) return "General";
  return props.resume.industry.charAt(0).toUpperCase() + props.resume.industry.slice(1);
});

const formattedWordCount = computed(() => {
  if (!props.resume.word_count) return "0";
  return props.resume.word_count.toLocaleString();
});

const formattedCreatedDate = computed(() =>
  formatDate(props.resume.created_at || props.resume.createdAt)
);

const formattedUpdatedDate = computed(() =>
  formatDate(props.resume.updated_at || props.resume.updatedAt)
);

const shouldShowUpdatedDate = computed(() => {
  const updated = props.resume.updated_at || props.resume.updatedAt;
  const created = props.resume.created_at || props.resume.createdAt;
  return updated && updated !== created;
});

const exportButtonClass = computed(() => {
  if (props.resume.export_status === "free") {
    return "border-primary-300 text-primary-700 bg-primary-50 hover:bg-primary-100";
  }
  return "border-green-300 text-green-700 bg-green-50 hover:bg-green-100";
});

const exportButtonText = computed(() => {
  if (isExporting.value) return "Exporting...";
  if (props.resume.export_status === "free") return "Export";
  return "Download";
});

// Helper functions
const formatDate = (date) => {
  if (!date) return "Unknown";
  try {
    return new Date(date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return "Unknown";
  }
};

// Event handlers
const viewResume = () => emit("view", props.resume);
const editResume = () => emit("edit", props.resume);
const duplicateResume = () => emit("duplicate", props.resume);

const exportResume = async () => {
  isExporting.value = true;
  try {
    await emit("export", props.resume);
  } finally {
    isExporting.value = false;
  }
};

const regenerateContent = () => {
  showMenu.value = false;
  emit("regenerate", props.resume);
};

const shareResume = () => {
  showMenu.value = false;
  emit("share", props.resume);
};

const deleteResume = () => {
  showMenu.value = false;
  if (isBrowser && confirm(`Are you sure you want to delete "${props.resume.title}"?`)) {
    emit("delete", props.resume);
  }
};

const toggleMenu = () => {
  showMenu.value = !showMenu.value;
};

// Click outside to close menu
const handleClickOutside = (event) => {
  if (isBrowser && menuContainer.value && !menuContainer.value.contains(event.target)) {
    showMenu.value = false;
  }
};

onMounted(() => {
  if (isBrowser) {
    document.addEventListener("click", handleClickOutside);
  }
});

onUnmounted(() => {
  if (isBrowser) {
    document.removeEventListener("click", handleClickOutside);
  }
});
</script>
