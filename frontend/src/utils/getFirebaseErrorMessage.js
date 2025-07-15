export const getFirebaseErrorMessage = (error) => {
  const code = error?.code || "";

  switch (code) {
    case "auth/email-already-in-use":
      return "This email is already registered.";
    case "auth/invalid-email":
      return "The email address is not valid.";
    case "auth/weak-password":
      return "The password is too weak.";
    case "auth/wrong-password":
      return "Incorrect password.";
    case "auth/user-not-found":
      return "No user found with this email.";
    case "auth/too-many-requests":
      return "Too many login attempts. Please try again later.";
    default:
      return "An unknown error occurred. Please try again.";
  }
};