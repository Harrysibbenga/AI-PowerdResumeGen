// Firebase utility functions
import { initializeApp } from "firebase/app";
import { getAuth, onAuthStateChanged, signOut } from "firebase/auth";

// Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.PUBLIC_FIREBASE_API_KEY,
  authDomain: import.meta.env.PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.PUBLIC_FIREBASE_APP_ID,
};

// Initialize Firebase only once
let app;
let auth;

try {
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
} catch (error) {
  console.error("Firebase initialization error:", error);
}

// Helper function to handle authentication state changes
function handleAuthStateChanged(loggedInElement, notLoggedInElement) {
  if (!auth) return;
  
  onAuthStateChanged(auth, (user) => {
    if (user) {
      // User is signed in
      loggedInElement?.classList.remove("hidden");
      notLoggedInElement?.classList.add("hidden");
    } else {
      // User is signed out
      loggedInElement?.classList.add("hidden");
      notLoggedInElement?.classList.remove("hidden");
    }
  });
}

// Helper function to handle logout
function handleLogout() {
  if (!auth) return;
  
  signOut(auth)
    .then(() => {
      window.location.href = "/";
    })
    .catch((error) => {
      console.error("Logout Error:", error);
    });
}

export { app, auth, handleAuthStateChanged, handleLogout };