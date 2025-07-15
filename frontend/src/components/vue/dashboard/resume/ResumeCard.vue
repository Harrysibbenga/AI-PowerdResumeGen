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
            <span class="font-medium">{{ resume.target_job_title }}</span>
            <span v-if="resume.target_job_role" class="mx-2">•</span>
            <span v-if="resume.target_job_role" class="text-gray-500">{{
              resume.target_job_role
            }}</span>
          </div>
          <div v-if="resume.target_company" class="text-sm text-blue-600 mb-2">
            <span class="inline-flex items-center">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 3a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                  clip-rule="evenodd"
                ></path>
              </svg>
              Targeting: {{ resume.target_company }}
            </span>
          </div>
        </div>

        <!-- Status Badge -->
        <div class="flex flex-col items-end space-y-2">
          <span
            :class="getStatusBadgeClass(resume.export_status)"
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
          >
            {{ getStatusText(resume.export_status) }}
          </span>
          <span
            :class="getTemplateBadgeClass(resume.template_id)"
            class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
          >
            {{ formatTemplate(resume.template_id) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Card Body -->
    <div class="p-4">
      <!-- Summary Excerpt -->
      <div v-if="resume.summary_excerpt" class="mb-3">
        <p class="text-sm text-gray-600 leading-relaxed">{{ resume.summary_excerpt }}</p>
      </div>

      <!-- Industry and Stats -->
      <div class="flex items-center justify-between text-sm text-gray-500 mb-4">
        <div class="flex items-center space-x-4">
          <span class="inline-flex items-center">
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z"
                clip-rule="evenodd"
              ></path>
              <path
                d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z"
              ></path>
            </svg>
            {{ formatIndustry(resume.industry) }}
          </span>
          <span class="inline-flex items-center">
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                clip-rule="evenodd"
              ></path>
            </svg>
            {{ resume.sections_count }} sections
          </span>
          <span v-if="resume.word_count" class="inline-flex items-center">
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clip-rule="evenodd"
              ></path>
            </svg>
            {{ formatWordCount(resume.word_count) }} words
          </span>
        </div>
      </div>

      <!-- Timestamps -->
      <div class="text-xs text-gray-400 mb-4">
        <div>Created: {{ formatDate(resume.created_at) }}</div>
        <div v-if="resume.updated_at && resume.updated_at !== resume.created_at">
          Updated: {{ formatDate(resume.updated_at) }}
        </div>
      </div>
    </div>

    <!-- Card Actions -->
    <div class="px-4 py-3 bg-gray-50 border-t border-gray-100 rounded-b-lg">
      <div class="flex items-center justify-between">
        <div class="flex space-x-2">
          <!-- View Button -->
          <button
            @click="viewResume"
            class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"></path>
              <path
                fill-rule="evenodd"
                d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                clip-rule="evenodd"
              ></path>
            </svg>
            View
          </button>

          <!-- Edit Button -->
          <button
            @click="editResume"
            class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path
                d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"
              ></path>
            </svg>
            Edit
          </button>

          <!-- Duplicate Button -->
          <button
            @click="duplicateResume"
            class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"></path>
              <path
                d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"
              ></path>
            </svg>
            Copy
          </button>
        </div>

        <!-- Export/Download Button -->
        <div class="flex space-x-2">
          <button
            @click="exportResume"
            :disabled="isExporting"
            :class="getExportButtonClass()"
            class="inline-flex items-center px-3 py-1.5 border shadow-sm text-xs font-medium rounded focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <svg
              v-if="!isExporting"
              class="w-4 h-4 mr-1"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                clip-rule="evenodd"
              ></path>
            </svg>
            <svg
              v-else
              class="animate-spin w-4 h-4 mr-1"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
              ></path>
            </svg>
            {{ getExportButtonText() }}
          </button>

          <!-- More Options Menu -->
          <div class="relative" ref="menuContainer">
            <button
              @click="toggleMenu"
              class="inline-flex items-center px-2 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"
                ></path>
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <div
              v-if="showMenu"
              class="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10"
            >
              <div class="py-1">
                <button
                  @click="regenerateContent"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <svg
                    class="w-4 h-4 inline mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                      clip-rule="evenodd"
                    ></path>
                  </svg>
                  Regenerate Content
                </button>
                <button
                  @click="shareResume"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <svg
                    class="w-4 h-4 inline mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"
                    ></path>
                  </svg>
                  Share Resume
                </button>
                <button
                  @click="deleteResume"
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <svg
                    class="w-4 h-4 inline mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                      clip-rule="evenodd"
                    ></path>
                  </svg>
                  Delete Resume
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";

export default {
  name: "ResumeCard",
  props: {
    resume: {
      type: Object,
      required: true,
    },
  },
  emits: ["view", "edit", "duplicate", "export", "regenerate", "share", "delete"],
  setup(props, { emit }) {
    const isExporting = ref(false);
    const showMenu = ref(false);
    const menuContainer = ref(null);

    // Helper methods
    const getStatusBadgeClass = (status) => {
      const classes = {
        free: "bg-gray-100 text-gray-800",
        paid: "bg-green-100 text-green-800",
        subscribed: "bg-blue-100 text-blue-800",
      };
      return classes[status] || "bg-gray-100 text-gray-800";
    };

    const getStatusText = (status) => {
      const texts = {
        free: "Free",
        paid: "Exported",
        subscribed: "Pro",
      };
      return texts[status] || "Free";
    };

    const getTemplateBadgeClass = (template) => {
      const classes = {
        modern: "bg-purple-100 text-purple-800",
        classic: "bg-blue-100 text-blue-800",
        creative: "bg-pink-100 text-pink-800",
        minimal: "bg-gray-100 text-gray-800",
        executive: "bg-indigo-100 text-indigo-800",
      };
      return classes[template] || "bg-gray-100 text-gray-800";
    };

    const formatTemplate = (template) => {
      return template.charAt(0).toUpperCase() + template.slice(1);
    };

    const formatIndustry = (industry) => {
      return industry.charAt(0).toUpperCase() + industry.slice(1);
    };

    const formatWordCount = (count) => {
      return count.toLocaleString();
    };

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    };

    const getExportButtonClass = () => {
      if (props.resume.export_status === "free") {
        return "border-primary-300 text-primary-700 bg-primary-50 hover:bg-primary-100";
      }
      return "border-green-300 text-green-700 bg-green-50 hover:bg-green-100";
    };

    const getExportButtonText = () => {
      if (isExporting.value) return "Exporting...";
      if (props.resume.export_status === "free") return "Export";
      return "Download";
    };

    // Event handlers
    const viewResume = () => {
      emit("view", props.resume);
    };

    const editResume = () => {
      emit("edit", props.resume);
    };

    const duplicateResume = () => {
      emit("duplicate", props.resume);
    };

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
      if (confirm(`Are you sure you want to delete "${props.resume.title}"?`)) {
        emit("delete", props.resume);
      }
    };

    const toggleMenu = () => {
      showMenu.value = !showMenu.value;
    };

    // Click outside to close menu
    const handleClickOutside = (event) => {
      if (menuContainer.value && !menuContainer.value.contains(event.target)) {
        showMenu.value = false;
      }
    };

    onMounted(() => {
      document.addEventListener("click", handleClickOutside);
    });

    onUnmounted(() => {
      document.removeEventListener("click", handleClickOutside);
    });

    return {
      isExporting,
      showMenu,
      menuContainer,
      getStatusBadgeClass,
      getStatusText,
      getTemplateBadgeClass,
      formatTemplate,
      formatIndustry,
      formatWordCount,
      formatDate,
      getExportButtonClass,
      getExportButtonText,
      viewResume,
      editResume,
      duplicateResume,
      exportResume,
      regenerateContent,
      shareResume,
      deleteResume,
      toggleMenu,
    };
  },
};
</script>
