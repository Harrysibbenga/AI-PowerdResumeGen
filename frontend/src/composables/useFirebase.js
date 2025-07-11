import { ref, computed } from "vue";
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { initFirebase } from "@/utils/firebase";

let firebaseApp = null;
let auth = null;

const user = ref(null);
const isLoading = ref(true);
const isAuthenticated = computed(() => !!user.value);
const authInitialized = ref(false);

let unsubscribe = null;

export const useFirebase = () => {
  const initAuth = async () => {
    try {
      firebaseApp = initFirebase();
      auth = getAuth(firebaseApp);

      if (unsubscribe) return;

      unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
        console.log("Auth state changed:", firebaseUser ? "User logged in" : "User logged out");
        user.value = firebaseUser;
        isLoading.value = false;
        authInitialized.value = true;
      });
    } catch (error) {
      console.error("Error initializing auth:", error);
      isLoading.value = false;
      authInitialized.value = true;
    }
  };

  const getFirebaseAuth = async () => {
    if (!auth) {
      firebaseApp = initFirebase();
      auth = getAuth(firebaseApp);
    }
    return auth;
  };

  const getCurrentUser = () => user.value;

  const waitForAuth = () => {
    return new Promise((resolve) => {
      if (authInitialized.value) {
        resolve(user.value);
        return;
      }

      const checkAuth = () => {
        if (authInitialized.value) {
          resolve(user.value);
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
  };

  return {
    user,
    isLoading,
    isAuthenticated,
    authInitialized,
    initAuth,
    getFirebaseAuth,
    getCurrentUser,
    waitForAuth,
    cleanup
  };
};
