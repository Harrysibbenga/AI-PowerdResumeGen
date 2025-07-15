<template>
  <div class="relative" ref="menuRef">
    <button
      @click="toggleDropdown"
      class="w-10 h-10 rounded-full bg-primary-600 text-white font-semibold flex items-center justify-center hover:bg-primary-700 transition-colors duration-200"
      :title="user?.displayName || user?.email || 'User'"
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
        <!-- User Info Header -->
        <div class="px-4 py-3 border-b border-gray-100">
          <p class="text-sm text-gray-900 font-medium truncate">
            {{ user?.displayName || "User" }}
          </p>
          <p class="text-xs text-gray-500 truncate">{{ user?.email }}</p>
        </div>

        <!-- Menu Items -->
        <div class="py-1">
          <a
            href="/dashboard"
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
            @click="closeDropdown"
          >
            Dashboard
          </a>
          <a
            href="/account"
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
            @click="closeDropdown"
          >
            Account Settings
          </a>
        </div>

        <!-- Logout Section -->
        <div class="border-t border-gray-100 py-1">
          <button
            @click="logout"
            :disabled="isLoggingOut"
            class="w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoggingOut" class="flex items-center">
              <div
                class="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600 mr-2"
              ></div>
              Logging out...
            </span>
            <span v-else>Log Out</span>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
});

const dropdownOpen = ref(false);
const menuRef = ref(null);
const isLoggingOut = ref(false);

const { getAuth } = useFirebase();
const { success, error: showError } = useToast();

const initials = computed(() => {
  if (!props.user) return "?";

  // Try displayName first, then email
  const name = props.user.displayName || props.user.email || "User";

  if (props.user.displayName) {
    // Use display name initials
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2); // Limit to 2 characters
  } else {
    // Use first letter of email
    return name[0].toUpperCase();
  }
});

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value;
}

function closeDropdown() {
  dropdownOpen.value = false;
}

function handleClickOutside(event) {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
    dropdownOpen.value = false;
  }
}

async function logout() {
  if (isLoggingOut.value) return;

  try {
    isLoggingOut.value = true;
    dropdownOpen.value = false;

    const auth = await getAuth();
    if (!auth) {
      throw new Error("Authentication not available");
    }

    // Import signOut dynamically to avoid SSR issues
    const { signOut } = await import("firebase/auth");
    await signOut(auth);

    success("Logged out successfully");

    // Small delay to show the success message
    setTimeout(() => {
      window.location.href = "/";
    }, 1000);
  } catch (err) {
    console.error("Logout error:", err);
    showError("Failed to log out. Please try again.");
  } finally {
    isLoggingOut.value = false;
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
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
