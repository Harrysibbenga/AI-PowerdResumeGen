<template>
  <div>
    <div v-if="isAuthenticated" class="flex items-center gap-4">
      <UserMenu :user="user" />
    </div>
    <div v-else class="flex items-center gap-3">
      <a href="/login" class="text-gray-700 hover:text-primary-600"> Log In </a>
      <a
        href="/register"
        class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg"
      >
        Sign Up
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { app } from "@/utils/firebase";
import UserMenu from "@/components/vue/common/UserMenu.vue";

const auth = getAuth(app);

const isAuthenticated = ref(false);
const user = ref(null);

onMounted(() => {
  onAuthStateChanged(auth, (u) => {
    if (u) {
      isAuthenticated.value = true;
      user.value = u;
    } else {
      isAuthenticated.value = false;
      user.value = null;
    }
  });
});
</script>
