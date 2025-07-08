import { ref, computed } from 'vue'
import { getAuth, onAuthStateChanged } from 'firebase/auth'

// Import your Firebase app configuration
let firebaseApp = null
let auth = null

// Initialize Firebase lazily
const initFirebase = async () => {
  if (firebaseApp) return firebaseApp

  try {
    // Dynamic import to ensure Firebase is only loaded on the client
    const { app } = await import('@/utils/firebase')
    firebaseApp = app
    auth = getAuth(firebaseApp)
    return firebaseApp
  } catch (error) {
    console.error('Failed to initialize Firebase:', error)
    throw error
  }
}

// Reactive user state
const user = ref(null)
const isLoading = ref(true)
const isAuthenticated = computed(() => !!user.value)
const authInitialized = ref(false)

// Auth state listener
let unsubscribe = null

export const useFirebase = () => {
  const initAuth = async () => {
    try {
      await initFirebase()
      
      if (unsubscribe) return // Already listening

      unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
        console.log('Auth state changed:', firebaseUser ? 'User logged in' : 'User logged out')
        user.value = firebaseUser
        isLoading.value = false
        authInitialized.value = true
      })
    } catch (error) {
      console.error('Error initializing auth:', error)
      isLoading.value = false
      authInitialized.value = true
    }
  }

  const getFirebaseAuth = async () => {
    await initFirebase()
    return auth
  }

  const getCurrentUser = () => {
    return user.value
  }

  const waitForAuth = () => {
    return new Promise((resolve) => {
      // If auth is already initialized, resolve immediately
      if (authInitialized.value) {
        resolve(user.value)
        return
      }

      // Otherwise, wait for auth to initialize
      const checkAuth = () => {
        if (authInitialized.value) {
          resolve(user.value)
        } else {
          setTimeout(checkAuth, 50)
        }
      }
      
      checkAuth()
    })
  }

  // Cleanup function
  const cleanup = () => {
    if (unsubscribe) {
      unsubscribe()
      unsubscribe = null
    }
  }

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
  }
}