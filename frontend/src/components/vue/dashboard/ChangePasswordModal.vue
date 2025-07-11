<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Change Password</h3>
      <form @submit.prevent="handleChangePassword">
        <div class="mb-4">
          <label
            for="current-password"
            class="block text-sm font-medium text-gray-700 mb-2"
            >Current Password</label
          >
          <input
            type="password"
            v-model="currentPassword"
            id="current-password"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Enter current password"
            required
          />
        </div>
        <div class="mb-4">
          <label for="new-password" class="block text-sm font-medium text-gray-700 mb-2"
            >New Password</label
          >
          <input
            type="password"
            v-model="newPassword"
            id="new-password"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Enter new password"
            required
          />
        </div>
        <div class="mb-6">
          <label
            for="confirm-password"
            class="block text-sm font-medium text-gray-700 mb-2"
            >Confirm New Password</label
          >
          <input
            type="password"
            v-model="confirmPassword"
            id="confirm-password"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Confirm new password"
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
            Change Password
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import {
  updatePassword,
  EmailAuthProvider,
  reauthenticateWithCredential,
} from "firebase/auth";

const props = defineProps({ user: Object });
const emit = defineEmits(["close", "success", "error"]);

const currentPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

const handleChangePassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    emit("error", "New passwords don't match");
    return;
  }

  if (newPassword.value.length < 6) {
    emit("error", "Password must be at least 6 characters");
    return;
  }

  try {
    const credential = EmailAuthProvider.credential(
      props.user.email,
      currentPassword.value
    );
    await reauthenticateWithCredential(props.user, credential);
    await updatePassword(props.user, newPassword.value);

    currentPassword.value = "";
    newPassword.value = "";
    confirmPassword.value = "";

    emit("success", "Password changed successfully!");
    emit("close");
  } catch (err) {
    if (err.code === "auth/wrong-password") {
      emit("error", "Current password is incorrect");
    } else if (err.code === "auth/requires-recent-login") {
      emit("error", "Please log out and log back in to change your password");
    } else {
      emit("error", err.message || "Failed to change password");
    }
  }
};
</script>
