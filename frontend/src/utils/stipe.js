// Stripe utilities for the frontend
import { getAuth } from 'firebase/auth';

/**
 * Create a checkout session for a one-time purchase
 * @param {string} resumeId - Resume ID to purchase
 * @param {string} successUrl - URL to redirect to on success
 * @param {string} cancelUrl - URL to redirect to on cancel
 * @returns {Promise<string>} - Checkout URL
 */
export async function createOneTimeCheckout(resumeId, successUrl, cancelUrl) {
  try {
    const auth = getAuth();
    const user = auth.currentUser;
    
    if (!user) {
      throw new Error('You must be logged in to make a purchase');
    }
    
    const idToken = await user.getIdToken();
    
    const response = await fetch('/api/v1/create-checkout-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify({
        resumeId,
        priceId: import.meta.env.PUBLIC_STRIPE_ONE_TIME_PRICE_ID,
        mode: 'payment',
        successUrl,
        cancelUrl
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create checkout session');
    }
    
    const data = await response.json();
    return data.url;
  } catch (error) {
    console.error('Error creating checkout session:', error);
    throw error;
  }
}

/**
 * Create a checkout session for a subscription
 * @param {string} successUrl - URL to redirect to on success
 * @param {string} cancelUrl - URL to redirect to on cancel
 * @returns {Promise<string>} - Checkout URL
 */
export async function createSubscriptionCheckout(successUrl, cancelUrl) {
  try {
    const auth = getAuth();
    const user = auth.currentUser;
    
    if (!user) {
      throw new Error('You must be logged in to subscribe');
    }
    
    const idToken = await user.getIdToken();
    
    const response = await fetch('/api/v1/create-checkout-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify({
        priceId: import.meta.env.PUBLIC_STRIPE_SUBSCRIPTION_PRICE_ID,
        mode: 'subscription',
        successUrl,
        cancelUrl
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create subscription checkout');
    }
    
    const data = await response.json();
    return data.url;
  } catch (error) {
    console.error('Error creating subscription checkout:', error);
    throw error;
  }
}

/**
 * Redirect to Stripe customer portal for subscription management
 * @param {string} returnUrl - URL to return to after managing subscription
 * @returns {Promise<void>}
 */
export async function redirectToCustomerPortal(returnUrl = window.location.href) {
  try {
    const auth = getAuth();
    const user = auth.currentUser;
    
    if (!user) {
      throw new Error('You must be logged in to manage your subscription');
    }
    
    const idToken = await user.getIdToken();
    
    const response = await fetch('/api/v1/create-portal-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify({
        returnUrl
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create portal session');
    }
    
    const data = await response.json();
    
    // Redirect to the Stripe Customer Portal
    window.location.href = data.url;
  } catch (error) {
    console.error('Error redirecting to customer portal:', error);
    throw error;
  }
}

/**
 * Check if the current user has an active subscription
 * @returns {Promise<boolean>} - Whether the user has an active subscription
 */
export async function checkSubscriptionStatus() {
  try {
    const auth = getAuth();
    const user = auth.currentUser;
    
    if (!user) {
      return false;
    }
    
    const idToken = await user.getIdToken();
    
    const response = await fetch('/api/v1/subscription-status', {
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    });
    
    if (!response.ok) {
      return false;
    }
    
    const data = await response.json();
    return data.isSubscribed;
  } catch (error) {
    console.error('Error checking subscription status:', error);
    return false;
  }
}