import { ref, computed } from "vue";
import { onAuthStateChanged } from "firebase/auth";
import { getFirebaseAuth } from "@/utils/firebase";

const user = ref(null);
const isLoading = ref(true);
const isAuthenticated = computed(() => !!user.value);
const authInitialized = ref(false);

// Check if we're in browser environment
const isBrowser = typeof window !== 'undefined';

let unsubscribe = null;
let isInitializing = false;

export const useFirebase = () => {
  const initAuth = async () => {
    // Skip initialization during SSR
    if (!isBrowser) {
      authInitialized.value = true;
      isLoading.value = false;
      return;
    }

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

  const getIdToken = async () => {
    if (!isBrowser) {
      throw new Error('Cannot get ID token during server-side rendering');
    }

    const currentUser = getCurrentUser();
    if (!currentUser) {
      throw new Error('User not authenticated');
    }

    try {
      return await currentUser.getIdToken();
    } catch (error) {
      console.error('Error getting ID token:', error);
      throw new Error('Failed to get authentication token');
    }
  };

  const waitForAuth = () => {
    return new Promise((resolve, reject) => {
      // If not in browser, resolve with null immediately
      if (!isBrowser) {
        resolve(null);
        return;
      }

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

  const signOut = async () => {
    if (!isBrowser) return;
    
    try {
      const auth = getAuth();
      const { signOut: firebaseSignOut } = await import('firebase/auth');
      await firebaseSignOut(auth);
      
      // Clear any stored resume data on logout
      localStorage.removeItem('resumeFormData');
      localStorage.removeItem('currentResumeId');
      localStorage.removeItem('editMode');
    } catch (error) {
      console.error('Error signing out:', error);
      throw error;
    }
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
    getIdToken,
    waitForAuth,
    signOut,
    cleanup
  };
};