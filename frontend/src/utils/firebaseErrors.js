// src/utils/firebaseErrors.js

export const firebaseErrorMessages = {
  // Auth errors
  "auth/email-already-in-use": "This email is already in use.",
  "auth/invalid-email": "The email address is not valid.",
  "auth/weak-password": "The password is too weak.",
  "auth/user-not-found": "No user found with this email.",
  "auth/wrong-password": "Incorrect password.",
  "auth/too-many-requests": "Too many attempts. Try again later.",
  "auth/network-request-failed": "Network error. Check your connection.",
  "auth/missing-password": "Password is required.",
  "auth/invalid-credential": "Invalid credentials provided.",
  // Add more as needed...
};

export function getFirebaseErrorMessage(error) {
  if (!error?.code) return "An unknown error occurred.";
  return firebaseErrorMessages[error.code] || "An unexpected error occurred.";
}
