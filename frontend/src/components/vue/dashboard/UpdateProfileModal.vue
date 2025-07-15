<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Update Profile</h3>
      <form @submit.prevent="updateDisplayName">
        <div class="mb-4">
          <label for="display-name" class="block text-sm font-medium text-gray-700 mb-2"
            >Display Name</label
          >
          <input
            type="text"
            v-model="displayName"
            id="display-name"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Enter your display name"
            required
          />
        </div>
        <div class="flex justify-end space-x-3">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Update
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { updateProfile } from "firebase/auth";

const props = defineProps({ user: Object });
const emit = defineEmits(["close", "success", "error"]);

const displayName = ref("");

watch(
  () => props.user,
  (user) => {
    displayName.value = user?.displayName || "";
  },
  { immediate: true }
);

const updateDisplayName = async () => {
  try {
    await updateProfile(props.user, {
      displayName: displayName.value,
    });
    emit("success", "Profile updated successfully!");
    emit("close");
  } catch (err) {
    emit("error", err.message || "Failed to update profile.");
  }
};
</script>
