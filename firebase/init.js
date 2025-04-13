// Firebase initialization for server
import * as admin from 'firebase-admin';
import { getFirestore } from 'firebase-admin/firestore';

// Initialize Firebase Admin SDK
let app;
try {
  app = admin.app();
} catch (e) {
  // Use service account credentials JSON
  const serviceAccount = process.env.FIREBASE_SERVICE_ACCOUNT 
    ? JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT)
    : require('./serviceAccount.json');
  
  app = admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
}

// Export Firestore instance and auth
const db = getFirestore(app);
const auth = admin.auth(app);

export { db, auth, admin };

/**
 * Verify Firebase ID token
 * @param {string} idToken - Firebase ID token
 * @returns {Promise<Object>} - User data
 */
export async function verifyIdToken(idToken) {
  try {
    return await auth.verifyIdToken(idToken);
  } catch (error) {
    console.error('Error verifying ID token:', error);
    throw new Error('Unauthorized: Invalid token');
  }
}

/**
 * Create or update a user in Firestore
 * @param {string} uid - User ID
 * @param {Object} userData - User data to store
 * @returns {Promise<void>}
 */
export async function createOrUpdateUser(uid, userData) {
  try {
    const userRef = db.collection('users').doc(uid);
    await userRef.set({
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
      ...userData
    }, { merge: true });
  } catch (error) {
    console.error('Error creating/updating user:', error);
    throw error;
  }
}

/**
 * Get user data from Firestore
 * @param {string} uid - User ID
 * @returns {Promise<Object|null>} - User data or null if not found
 */
export async function getUserData(uid) {
  try {
    const userDoc = await db.collection('users').doc(uid).get();
    if (!userDoc.exists) {
      return null;
    }
    return userDoc.data();
  } catch (error) {
    console.error('Error getting user data:', error);
    throw error;
  }
}