<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h2 class="text-xl font-semibold mb-4">Account Settings</h2>
    <div class="flex flex-col md:flex-row md:items-center justify-between">
      <div>
        <p class="text-gray-700 font-medium">Email: {{ user?.email }}</p>
        <p class="text-gray-700 font-medium">
          Name: {{ user?.displayName || "Not set" }}
        </p>
      </div>
      <div class="mt-4 md:mt-0">
        <button
          @click="showUpdate = true"
          class="text-primary-600 hover:text-primary-800 mr-4"
        >
          Update Profile
        </button>
        <button
          @click="showPassword = true"
          class="text-primary-600 hover:text-primary-800"
        >
          Change Password
        </button>
      </div>
    </div>

    <UpdateProfileModal
      v-if="showUpdate"
      :user="user"
      @close="showUpdate = false"
      @success="$emit('update-success', $event)"
      @error="$emit('update-error', $event)"
    />
    <ChangePasswordModal
      v-if="showPassword"
      :user="user"
      @close="showPassword = false"
      @success="$emit('update-success', $event)"
      @error="$emit('update-error', $event)"
    />
  </div>
</template>

<script setup>
import { ref } from "vue";
import UpdateProfileModal from "@/components/vue/dashboard/UpdateProfileModal.vue";
import ChangePasswordModal from "@/components/vue/dashboard/ChangePasswordModal.vue";

defineProps({ user: Object });

const showUpdate = ref(false);
const showPassword = ref(false);
</script>
