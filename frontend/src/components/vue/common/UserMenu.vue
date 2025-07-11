<template>
  <div class="relative" ref="menuRef">
    <button
      @click="toggleDropdown"
      class="w-10 h-10 rounded-full bg-primary-600 text-white font-semibold flex items-center justify-center"
      :title="user?.displayName || 'User'"
    >
      <span v-if="user?.photoURL">
        <img
          :src="user.photoURL"
          alt="Profile"
          class="w-10 h-10 rounded-full object-cover"
        />
      </span>
      <span v-else>
        {{ initials }}
      </span>
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
        v-if="dropdownOpen"
        class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
      >
        <a href="/dashboard" class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >Dashboard</a
        >
        <a
          href="/account"
          class="block px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
        >
          Account Settings
        </a>
        <button
          @click="logout"
          class="w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100 transition-colors"
        >
          Log Out
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import { signOut } from "firebase/auth";
import Toast from "vue-toast-notification";

const props = defineProps({
  user: Object, // Accept user from parent
});

const dropdownOpen = ref(false);
const menuRef = ref(null);
const toast = Toast.useToast();

const initials = computed(() => {
  if (!props.user?.displayName) return "?";
  return props.user.displayName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase();
});

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value;
}

function handleClickOutside(event) {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
    dropdownOpen.value = false;
  }
}

async function logout() {
  try {
    const { getAuth } = await import("firebase/auth");
    const auth = getAuth();
    await signOut(auth);
    toast.success("Logged out successfully");
    window.location.href = "/";
  } catch (err) {
    console.error("Logout error:", err);
    toast.error("Failed to log out");
  }
}

onMounted(() => document.addEventListener("click", handleClickOutside));
onBeforeUnmount(() => document.removeEventListener("click", handleClickOutside));
</script>
