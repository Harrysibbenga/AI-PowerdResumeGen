import { ref, computed } from "vue";
import { onAuthStateChanged } from "firebase/auth";
import { getFirebaseAuth } from "@/utils/firebase";

const user = ref(null);
const isLoading = ref(true);
const isAuthenticated = computed(() => !!user.value);
const authInitialized = ref(false);

let unsubscribe = null;
let isInitializing = false;

export const useFirebase = () => {
  const initAuth = async () => {
    if (authInitialized.value || isInitializing) {
      return;
    }

    isInitializing = true;

    try {
      console.log('Initializing Firebase auth...');
      const auth = getFirebaseAuth();

      if (unsubscribe) {
        unsubscribe();
      }

      unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
        console.log("Auth state changed:", firebaseUser ? "User logged in" : "User logged out");
        user.value = firebaseUser;
        isLoading.value = false;
        authInitialized.value = true;
        isInitializing = false;
      });

      console.log('Firebase auth initialized successfully');
    } catch (error) {
      console.error("Error initializing auth:", error);
      isLoading.value = false;
      authInitialized.value = true;
      isInitializing = false;
      throw error;
    }
  };

  const getAuth = () => {
    try {
      return getFirebaseAuth();
    } catch (error) {
      console.error("Error getting Firebase auth:", error);
      throw error;
    }
  };

  const getCurrentUser = () => user.value;

  const waitForAuth = () => {
    return new Promise((resolve, reject) => {
      if (authInitialized.value) {
        resolve(user.value);
        return;
      }

      let attempts = 0;
      const maxAttempts = 100; // 5 seconds max wait

      const checkAuth = () => {
        attempts++;
        
        if (authInitialized.value) {
          resolve(user.value);
        } else if (attempts >= maxAttempts) {
          reject(new Error('Auth initialization timeout'));
        } else {
          setTimeout(checkAuth, 50);
        }
      };

      checkAuth();
    });
  };

  const cleanup = () => {
    if (unsubscribe) {
      unsubscribe();
      unsubscribe = null;
    }
    authInitialized.value = false;
    isInitializing = false;
  };

  return {
    user,
    isLoading,
    isAuthenticated,
    authInitialized,
    initAuth,
    getAuth,
    getCurrentUser,
    waitForAuth,
    cleanup
  };
};