<template>
  <div
    class="border border-gray-200 rounded-lg p-6 flex flex-col h-64 hover:shadow-md transition-shadow group"
  >
    <!-- Header -->
    <div class="flex justify-between items-start mb-4">
      <h3 class="font-semibold text-lg text-gray-900 truncate flex-1 mr-2">
        {{ resume.title || "Untitled Resume" }}
      </h3>
      <span
        class="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded whitespace-nowrap"
      >
        {{ resume.industry || "General" }}
      </span>
    </div>

    <!-- Summary -->
    <p class="text-gray-600 text-sm flex-grow line-clamp-3 mb-4">
      {{ resume.summary || "No summary available" }}
    </p>

    <!-- Footer -->
    <div class="mt-auto pt-4 border-t border-gray-100">
      <div class="flex justify-between items-center mb-3">
        <span class="text-xs text-gray-500">
          {{ formatDate(resume.updated_at) }}
        </span>
        <div class="flex items-center space-x-1">
          <span class="w-2 h-2 rounded-full" :class="statusColor"></span>
          <span class="text-xs text-gray-500">{{ resume.status || "Draft" }}</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-between items-center">
        <div class="flex space-x-2">
          <a
            :href="`/builder?id=${resume.id}`"
            class="text-primary-600 hover:text-primary-800 text-sm font-medium transition-colors"
          >
            Edit
          </a>
          <a
            :href="`/preview?id=${resume.id}`"
            class="text-primary-600 hover:text-primary-800 text-sm font-medium transition-colors"
          >
            Preview
          </a>
        </div>

        <!-- Dropdown Menu -->
        <div class="relative">
          <button
            @click="toggleDropdown"
            class="p-1 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"
              ></path>
            </svg>
          </button>

          <div
            v-if="showDropdown"
            class="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10"
          >
            <div class="py-1">
              <button
                @click="duplicateResume"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Duplicate
              </button>
              <button
                @click="downloadResume"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Download PDF
              </button>
              <button
                @click="shareResume"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Share Link
              </button>
              <hr class="my-1" />
              <button
                @click="confirmDelete"
                class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showDeleteModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4" @click.stop>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">Delete Resume</h3>
        <p class="text-gray-600 mb-6">
          Are you sure you want to delete "{{ resume.title || "Untitled Resume" }}"? This
          action cannot be undone.
        </p>
        <div class="flex justify-end space-x-3">
          <button
            @click="showDeleteModal = false"
            class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleDelete"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from "vue";

export default {
  name: "ResumeCard",
  props: {
    resume: {
      type: Object,
      required: true,
    },
  },
  emits: ["delete"],
  setup(props, { emit }) {
    const showDropdown = ref(false);
    const showDeleteModal = ref(false);

    const statusColor = computed(() => {
      switch (props.resume.status) {
        case "Published":
          return "bg-green-400";
        case "Draft":
          return "bg-yellow-400";
        case "Archived":
          return "bg-gray-400";
        default:
          return "bg-gray-400";
      }
    });

    const formatDate = (dateString) => {
      if (!dateString) return "N/A";

      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays === 1) return "Yesterday";
      if (diffDays <= 7) return `${diffDays} days ago`;
      if (diffDays <= 30) return `${Math.ceil(diffDays / 7)} weeks ago`;

      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    };

    const toggleDropdown = () => {
      showDropdown.value = !showDropdown.value;
    };

    const closeDropdown = (event) => {
      if (!event.target.closest(".relative")) {
        showDropdown.value = false;
      }
    };

    const confirmDelete = () => {
      showDropdown.value = false;
      showDeleteModal.value = true;
    };

    const handleDelete = () => {
      emit("delete", props.resume.id);
      showDeleteModal.value = false;
    };

    const duplicateResume = () => {
      // Implement duplicate functionality
      console.log("Duplicate resume:", props.resume.id);
      showDropdown.value = false;
    };

    const downloadResume = () => {
      // Implement download functionality
      console.log("Download resume:", props.resume.id);
      showDropdown.value = false;
    };

    const shareResume = () => {
      // Implement share functionality
      console.log("Share resume:", props.resume.id);
      showDropdown.value = false;
    };

    onMounted(() => {
      document.addEventListener("click", closeDropdown);
    });

    onUnmounted(() => {
      document.removeEventListener("click", closeDropdown);
    });

    return {
      showDropdown,
      showDeleteModal,
      statusColor,
      formatDate,
      toggleDropdown,
      confirmDelete,
      handleDelete,
      duplicateResume,
      downloadResume,
      shareResume,
    };
  },
};
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
