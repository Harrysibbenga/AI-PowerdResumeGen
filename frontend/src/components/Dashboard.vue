<template>
  <div class="dashboard">
    <div class="header mb-10">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold">My Resumes</h1>
          <p class="text-gray-600">Manage and export your professional resumes</p>
        </div>

        <div class="flex items-center gap-4">
          <span
            v-if="isSubscribed"
            class="inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
          >
            Pro Subscription
          </span>
          <button
            @click="navigateToBuilder"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            New Resume
          </button>
          <button
            v-if="isSubscribed"
            @click="manageSubscription"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
          >
            Manage Subscription
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div
        class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"
      ></div>
      <p class="mt-4 text-gray-600">Loading your resumes...</p>
    </div>

    <div
      v-else-if="resumes.length === 0"
      class="text-center py-12 bg-white rounded-lg shadow-sm"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-16 w-16 mx-auto text-gray-400 mb-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <h3 class="text-xl font-medium mb-2">No resumes yet</h3>
      <p class="text-gray-500 mb-6">Create your first resume to get started</p>
      <button
        @click="navigateToBuilder"
        class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Create Your First Resume
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="resume in resumes"
        :key="resume.id"
        class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-bold text-lg mb-1">
              {{ resume.profile_data?.name || "Untitled Resume" }}
            </h3>
            <p class="text-sm text-gray-500 mb-2">
              {{ formatIndustry(resume.industry) }} • Created
              {{ formatDate(resume.created_at) }}
            </p>
            <div class="flex gap-2 mt-3">
              <button
                @click="viewResume(resume.id)"
                class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
              >
                View & Edit
              </button>
              <button
                @click="exportResume(resume.id)"
                class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
              >
                Export
              </button>
              <button
                @click="deleteResume(resume.id)"
                class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm"
              >
                Delete
              </button>
            </div>
          </div>

          <div class="status-badge">
            <span
              v-if="
                resume.export_status === 'paid' || resume.export_status === 'subscribed'
              "
              class="inline-block px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs"
            >
              Exported
            </span>
            <span
              v-else
              class="inline-block px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs"
            >
              Draft
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white p-6 rounded-lg max-w-md w-full">
        <h3 class="text-xl font-bold mb-4">Delete Resume</h3>
        <p class="mb-6">
          Are you sure you want to delete this resume? This action cannot be undone.
        </p>
        <div class="flex justify-end gap-3">
          <button
            @click="showDeleteModal = false"
            class="px-4 py-2 border rounded text-gray-600 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="confirmDelete"
            class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { getAuth, onAuthStateChanged } from "firebase/auth";
import {
  getFirestore,
  collection,
  query,
  where,
  orderBy,
  getDocs,
  doc,
  deleteDoc,
} from "firebase/firestore";
import { redirectToCustomerPortal } from "../utils/stripe";

export default {
  props: {
    isSubscribed: {
      type: Boolean,
      default: false,
    },
  },

  setup(props, { emit }) {
    const auth = getAuth();
    const db = getFirestore();

    const loading = ref(true);
    const resumes = ref([]);
    const showDeleteModal = ref(false);
    const resumeToDelete = ref(null);

    const loadUserResumes = async (userId) => {
      try {
        loading.value = true;

        const resumesQuery = query(
          collection(db, "resumes"),
          where("user_id", "==", userId),
          orderBy("created_at", "desc")
        );

        const querySnapshot = await getDocs(resumesQuery);

        if (querySnapshot.empty) {
          resumes.value = [];
        } else {
          resumes.value = querySnapshot.docs.map((doc) => {
            const data = doc.data();
            return {
              id: doc.id,
              ...data,
            };
          });
        }
      } catch (error) {
        console.error("Error loading resumes:", error);
        emit("error", "Failed to load resumes. Please try again.");
      } finally {
        loading.value = false;
      }
    };

    const navigateToBuilder = () => {
      window.location.href = "/builder";
    };

    const viewResume = (resumeId) => {
      window.location.href = `/resume/${resumeId}`;
    };

    const exportResume = (resumeId) => {
      window.location.href = `/resume/${resumeId}?export=true`;
    };

    const deleteResume = (resumeId) => {
      resumeToDelete.value = resumeId;
      showDeleteModal.value = true;
    };

    const confirmDelete = async () => {
      try {
        if (!resumeToDelete.value) return;

        await deleteDoc(doc(db, "resumes", resumeToDelete.value));

        // Update the local list
        resumes.value = resumes.value.filter((r) => r.id !== resumeToDelete.value);

        showDeleteModal.value = false;
        resumeToDelete.value = null;

        emit("success", "Resume deleted successfully");
      } catch (error) {
        console.error("Error deleting resume:", error);
        emit("error", "Failed to delete resume. Please try again.");
      }
    };

    const manageSubscription = async () => {
      try {
        await redirectToCustomerPortal();
      } catch (error) {
        console.error("Error redirecting to customer portal:", error);
        emit("error", "Failed to access subscription management. Please try again.");
      }
    };

    const formatDate = (timestamp) => {
      if (!timestamp) return "Unknown date";

      try {
        // Handle both Firestore Timestamp and regular Date objects
        const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);

        return date.toLocaleDateString("en-US", {
          year: "numeric",
          month: "short",
          day: "numeric",
        });
      } catch (e) {
        return "Invalid date";
      }
    };

    const formatIndustry = (industry) => {
      if (!industry) return "General";

      return industry.charAt(0).toUpperCase() + industry.slice(1);
    };

    onMounted(() => {
      const unsubscribe = onAuthStateChanged(auth, (user) => {
        if (user) {
          loadUserResumes(user.uid);
        } else {
          loading.value = false;
          resumes.value = [];
        }
      });

      // Cleanup subscription
      return () => unsubscribe();
    });

    return {
      loading,
      resumes,
      showDeleteModal,
      navigateToBuilder,
      viewResume,
      exportResume,
      deleteResume,
      confirmDelete,
      manageSubscription,
      formatDate,
      formatIndustry,
    };
  },
};
</script>
