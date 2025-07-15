<template>
  <div
    class="border border-gray-200 rounded-lg p-6 flex flex-col h-64 hover:shadow-md transition-shadow group bg-white"
  >
    <!-- Header -->
    <div class="flex justify-between items-start mb-4">
      <h3 class="font-semibold text-lg text-gray-900 truncate flex-1 mr-2">
        {{ resume.title || resume.name || "Untitled Resume" }}
      </h3>
      <span
        class="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded whitespace-nowrap"
      >
        {{ resume.industry || resume.job_title || "General" }}
      </span>
    </div>

    <!-- Summary -->
    <p class="text-gray-600 text-sm flex-grow line-clamp-3 mb-4">
      {{ resume.summary || resume.description || "No summary available" }}
    </p>

    <!-- Footer -->
    <div class="mt-auto pt-4 border-t border-gray-100">
      <div class="flex justify-between items-center mb-3">
        <span class="text-xs text-gray-500">
          {{ formatDate(resume.updated_at || resume.created_at) }}
        </span>
        <div class="flex items-center space-x-1">
          <span class="w-2 h-2 rounded-full" :class="statusColor"></span>
          <span class="text-xs text-gray-500 capitalize">{{ displayStatus }}</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-between items-center">
        <div class="flex space-x-2">
          <a
            :href="`/builder?id=${resume.id}`"
            class="text-primary-600 hover:text-primary-800 text-sm font-medium transition-colors"
            @click.stop
          >
            Edit
          </a>
          <a
            :href="`/preview?id=${resume.id}`"
            class="text-primary-600 hover:text-primary-800 text-sm font-medium transition-colors"
            @click.stop
          >
            Preview
          </a>
        </div>

        <!-- Dropdown Menu -->
        <div class="relative" ref="dropdownRef">
          <button
            @click.stop="toggleDropdown"
            class="p-1 text-gray-400 hover:text-gray-600 transition-colors rounded hover:bg-gray-100"
            :class="{ 'bg-gray-100': showDropdown }"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"
              ></path>
            </svg>
          </button>

          <transition
            enter-active-class="transition ease-out duration-100"
            enter-from-class="transform opacity-0 scale-95"
            enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75"
            leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95"
          >
            <div
              v-if="showDropdown"
              class="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10"
            >
              <div class="py-1">
                <button
                  @click="duplicateResume"
                  :disabled="isLoading"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                    ></path>
                  </svg>
                  Duplicate
                </button>
                <button
                  @click="downloadResume"
                  :disabled="isLoading"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    ></path>
                  </svg>
                  <span v-if="isLoading && loadingAction === 'download'"
                    >Downloading...</span
                  >
                  <span v-else>Download PDF</span>
                </button>
                <button
                  @click="shareResume"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors flex items-center"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"
                    ></path>
                  </svg>
                  Share Link
                </button>
                <hr class="my-1" />
                <button
                  @click="confirmDelete"
                  :disabled="isLoading"
                  class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    ></path>
                  </svg>
                  Delete
                </button>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="showDeleteModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click="showDeleteModal = false"
      >
        <transition
          enter-active-class="transition ease-out duration-300"
          enter-from-class="opacity-0 transform scale-95"
          enter-to-class="opacity-100 transform scale-100"
          leave-active-class="transition ease-in duration-200"
          leave-from-class="opacity-100 transform scale-100"
          leave-to-class="opacity-0 transform scale-95"
        >
          <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4" @click.stop>
            <div class="flex items-center mb-4">
              <div
                class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100"
              >
                <svg
                  class="h-6 w-6 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                  ></path>
                </svg>
              </div>
            </div>
            <div class="text-center">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Delete Resume</h3>
              <p class="text-gray-600 mb-6">
                Are you sure you want to delete "{{
                  resume.title || resume.name || "Untitled Resume"
                }}"? This action cannot be undone.
              </p>
            </div>
            <div class="flex justify-center space-x-3">
              <button
                @click="showDeleteModal = false"
                :disabled="isLoading"
                class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                @click="handleDelete"
                :disabled="isLoading"
                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center"
              >
                <span
                  v-if="isLoading && loadingAction === 'delete'"
                  class="flex items-center"
                >
                  <div
                    class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"
                  ></div>
                  Deleting...
                </span>
                <span v-else>Delete</span>
              </button>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";

const props = defineProps({
  resume: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["delete", "duplicate"]);

const showDropdown = ref(false);
const showDeleteModal = ref(false);
const dropdownRef = ref(null);
const isLoading = ref(false);
const loadingAction = ref(null);

const { waitForAuth } = useFirebase();
const { success, error: showError } = useToast();

const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

// Computed properties
const statusColor = computed(() => {
  const status = props.resume.status?.toLowerCase() || "draft";
  switch (status) {
    case "published":
    case "completed":
      return "bg-green-400";
    case "draft":
    case "in_progress":
      return "bg-yellow-400";
    case "archived":
      return "bg-gray-400";
    default:
      return "bg-blue-400";
  }
});

const displayStatus = computed(() => {
  return props.resume.status || "Draft";
});

// Helper methods
const formatDate = (dateString) => {
  if (!dateString) return "N/A";

  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays <= 7) return `${diffDays} days ago`;
    if (diffDays <= 30) return `${Math.ceil(diffDays / 7)} weeks ago`;

    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return "N/A";
  }
};

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

const closeDropdown = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    showDropdown.value = false;
  }
};

const confirmDelete = () => {
  showDropdown.value = false;
  showDeleteModal.value = true;
};

const handleDelete = async () => {
  try {
    isLoading.value = true;
    loadingAction.value = "delete";

    await new Promise((resolve) => setTimeout(resolve, 500)); // Small delay for UX

    emit("delete", props.resume.id);
    showDeleteModal.value = false;
    success("Resume deleted successfully");
  } catch (error) {
    showError("Failed to delete resume");
  } finally {
    isLoading.value = false;
    loadingAction.value = null;
  }
};

const duplicateResume = async () => {
  try {
    isLoading.value = true;
    loadingAction.value = "duplicate";
    showDropdown.value = false;

    const user = await waitForAuth();
    if (!user) {
      showError("Please log in to duplicate resumes");
      return;
    }

    const token = await user.getIdToken();
    const response = await fetch(
      `${API_URL}/api/v1/resume/${props.resume.id}/duplicate`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to duplicate resume");
    }

    const duplicatedResume = await response.json();
    emit("duplicate", duplicatedResume);
    success("Resume duplicated successfully");
  } catch (error) {
    console.error("Error duplicating resume:", error);
    showError("Failed to duplicate resume");
  } finally {
    isLoading.value = false;
    loadingAction.value = null;
  }
};

const downloadResume = async () => {
  try {
    isLoading.value = true;
    loadingAction.value = "download";
    showDropdown.value = false;

    const user = await waitForAuth();
    if (!user) {
      showError("Please log in to download resumes");
      return;
    }

    const token = await user.getIdToken();
    const response = await fetch(`${API_URL}/api/v1/resume/${props.resume.id}/download`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to generate PDF");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${props.resume.title || props.resume.name || "resume"}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    success("Resume downloaded successfully");
  } catch (error) {
    console.error("Error downloading resume:", error);
    showError("Failed to download resume");
  } finally {
    isLoading.value = false;
    loadingAction.value = null;
  }
};

const shareResume = async () => {
  try {
    showDropdown.value = false;

    const shareUrl = `${window.location.origin}/preview?id=${props.resume.id}`;

    if (navigator.share) {
      await navigator.share({
        title: props.resume.title || props.resume.name || "My Resume",
        text: "Check out my resume",
        url: shareUrl,
      });
    } else {
      // Fallback to clipboard
      await navigator.clipboard.writeText(shareUrl);
      success("Resume link copied to clipboard");
    }
  } catch (error) {
    if (error.name !== "AbortError") {
      console.error("Error sharing resume:", error);
      showError("Failed to share resume");
    }
  }
};

// Lifecycle
onMounted(() => {
  document.addEventListener("click", closeDropdown);
});

onUnmounted(() => {
  document.removeEventListener("click", closeDropdown);
});
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

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
