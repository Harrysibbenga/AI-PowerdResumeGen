import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

let firebaseApp = null;
let auth = null;

const firebaseConfig = {
  apiKey: import.meta.env.PUBLIC_FIREBASE_API_KEY,
  authDomain: import.meta.env.PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.PUBLIC_FIREBASE_APP_ID,
};

export const initFirebase = () => {
  if (!firebaseApp) {
    // Validate required config
    const requiredKeys = ['apiKey', 'authDomain', 'projectId'];
    const missingKeys = requiredKeys.filter(key => !firebaseConfig[key]);
    
    if (missingKeys.length > 0) {
      throw new Error(`Missing Firebase config: ${missingKeys.join(', ')}`);
    }

    console.log('Initializing Firebase...');
    firebaseApp = initializeApp(firebaseConfig);
    auth = getAuth(firebaseApp);
    console.log('Firebase initialized successfully');
  }
  return firebaseApp;
};

export const getFirebaseAuth = () => {
  if (!auth) {
    initFirebase();
  }
  return auth;
};

// Initialize Firebase immediately when this module is imported
initFirebase();