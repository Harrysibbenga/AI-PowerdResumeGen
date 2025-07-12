import { signInWithEmailAndPassword, signOut } from "firebase/auth";
import { getFirebaseAuth } from "@/utils/firebase";
import { API_BASE_URL } from "../../utils/api";
import axios from "axios";

class AuthClient {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api/v1/auth`
    });
  }

  getAuth() {
    return getFirebaseAuth();
  }

  async login(email, password, rememberMe = false) {
    try {
      const auth = this.getAuth();
      console.log('Attempting Firebase login...');
      
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const idToken = await userCredential.user.getIdToken();

      console.log('Firebase login successful, calling backend...');
      
      const res = await this.api.post("/login", {
        id_token: idToken,
        remember_me: rememberMe
      });

      if (res.data.requires_2fa) {
        return {
          status: "2fa_required",
          user: res.data.user
        };
      }

      this._storeTokens(res.data);
      return {
        status: "success",
        user: res.data.user
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async loginWith2FA(idToken, twoFactorCode, rememberMe = false) {
    try {
      const res = await this.api.post("/login/2fa", {
        id_token: idToken,
        two_factor_code: twoFactorCode,
        remember_me: rememberMe
      });

      this._storeTokens(res.data);
      return {
        status: "success",
        user: res.data.user
      };
    } catch (error) {
      console.error('2FA login error:', error);
      throw error;
    }
  }

  async refreshToken(refreshToken) {
    try {
      const res = await this.api.post("/refresh", {
        refresh_token: refreshToken
      });

      this._storeTokens(res.data);
      return res.data;
    } catch (error) {
      console.error('Token refresh error:', error);
      throw error;
    }
  }

  async logoutAllDevices() {
    try {
      await this.api.post("/logout/all", {}, {
        headers: {
          Authorization: `Bearer ${this.getAccessToken()}`
        }
      });

      const auth = this.getAuth();
      await signOut(auth);
      this._clearTokens();
    } catch (error) {
      console.error('Logout error:', error);
      // Clear tokens even if API call fails
      this._clearTokens();
      throw error;
    }
  }

  // =================== PASSWORD MANAGEMENT METHODS ===================

  /**
   * Request password reset email
   * @param {string} email - User's email address
   * @returns {Promise<{message: string}>}
   */
  async forgotPassword(email) {
    try {
      console.log('Requesting password reset for:', email);
      
      const res = await this.api.post("/forgot-password", {
        email: email
      });

      console.log('Password reset request successful');
      return res.data;
    } catch (error) {
      console.error('Forgot password error:', error);
      throw error;
    }
  }

  /**
   * Reset password using token from email
   * @param {string} token - Reset token from email
   * @param {string} newPassword - New password
   * @returns {Promise<{message: string}>}
   */
  async resetPassword(token, newPassword) {
    try {
      console.log('Resetting password with token...');
      
      const res = await this.api.post("/reset-password", {
        token: token,
        newPassword: newPassword
      });

      console.log('Password reset successful');
      return res.data;
    } catch (error) {
      console.error('Reset password error:', error);
      throw error;
    }
  }

  /**
   * Change password for authenticated user
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   * @returns {Promise<{message: string}>}
   */
  async changePassword(currentPassword, newPassword) {
    try {
      console.log('Changing password for authenticated user...');
      
      const res = await this.api.put("/change-password", {
        current_password: currentPassword,
        new_password: newPassword
      }, {
        headers: {
          Authorization: `Bearer ${this.getAccessToken()}`
        }
      });

      console.log('Password change successful');
      return res.data;
    } catch (error) {
      console.error('Change password error:', error);
      throw error;
    }
  }

  /**
   * Validate password strength in real-time
   * @param {string} password - Password to validate
   * @returns {Promise<{score: number, strength: string, is_strong: boolean, suggestions: string[]}>}
   */
  async validatePasswordStrength(password) {
    try {
      const res = await this.api.post("/validate-password", {
        password: password
      });

      return res.data;
    } catch (error) {
      console.error('Password validation error:', error);
      throw error;
    }
  }

  // =================== UTILITY METHODS FOR PASSWORD FLOWS ===================

  /**
   * Complete password reset flow with validation
   * @param {string} token - Reset token
   * @param {string} newPassword - New password
   * @param {string} confirmPassword - Password confirmation
   * @returns {Promise<{success: boolean, message: string, errors?: string[]}>}
   */
  async completePasswordReset(token, newPassword, confirmPassword) {
    try {
      // Client-side validation
      const errors = [];

      if (!token) {
        errors.push("Reset token is required");
      }

      if (!newPassword) {
        errors.push("New password is required");
      }

      if (!confirmPassword) {
        errors.push("Password confirmation is required");
      }

      if (newPassword !== confirmPassword) {
        errors.push("Passwords do not match");
      }

      if (errors.length > 0) {
        return {
          success: false,
          message: "Validation failed",
          errors: errors
        };
      }

      // Validate password strength
      const strengthValidation = await this.validatePasswordStrength(newPassword);
      if (!strengthValidation.is_strong) {
        return {
          success: false,
          message: "Password does not meet security requirements",
          errors: strengthValidation.suggestions
        };
      }

      // Reset password
      const result = await this.resetPassword(token, newPassword);
      
      return {
        success: true,
        message: result.message
      };

    } catch (error) {
      console.error('Complete password reset error:', error);
      
      // Handle different error types
      if (error.response?.status === 400) {
        return {
          success: false,
          message: error.response.data.detail || "Invalid request",
          errors: error.response.data.suggestions || []
        };
      }

      return {
        success: false,
        message: "An unexpected error occurred. Please try again.",
        errors: []
      };
    }
  }

  /**
   * Complete password change flow with validation
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   * @param {string} confirmPassword - Password confirmation
   * @returns {Promise<{success: boolean, message: string, errors?: string[]}>}
   */
  async completePasswordChange(currentPassword, newPassword, confirmPassword) {
    try {
      // Client-side validation
      const errors = [];

      if (!currentPassword) {
        errors.push("Current password is required");
      }

      if (!newPassword) {
        errors.push("New password is required");
      }

      if (!confirmPassword) {
        errors.push("Password confirmation is required");
      }

      if (newPassword !== confirmPassword) {
        errors.push("Passwords do not match");
      }

      if (currentPassword === newPassword) {
        errors.push("New password must be different from current password");
      }

      if (errors.length > 0) {
        return {
          success: false,
          message: "Validation failed",
          errors: errors
        };
      }

      // Validate password strength
      const strengthValidation = await this.validatePasswordStrength(newPassword);
      if (!strengthValidation.is_strong) {
        return {
          success: false,
          message: "Password does not meet security requirements",
          errors: strengthValidation.suggestions
        };
      }

      // Change password
      const result = await this.changePassword(currentPassword, newPassword);
      
      return {
        success: true,
        message: result.message
      };

    } catch (error) {
      console.error('Complete password change error:', error);
      
      // Handle different error types
      if (error.response?.status === 400) {
        return {
          success: false,
          message: error.response.data.detail || "Invalid request",
          errors: error.response.data.suggestions || []
        };
      }

      if (error.response?.status === 401) {
        return {
          success: false,
          message: "Current password is incorrect",
          errors: []
        };
      }

      return {
        success: false,
        message: "An unexpected error occurred. Please try again.",
        errors: []
      };
    }
  }

  // =================== EXISTING METHODS ===================

  getCurrentUser() {
    const auth = this.getAuth();
    return auth?.currentUser ?? null;
  }

  getAccessToken() {
    return localStorage.getItem("access_token");
  }

  getRefreshToken() {
    return localStorage.getItem("refresh_token");
  }

  _storeTokens(data) {
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
  }

  _clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  // =================== HELPER METHODS ===================

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!this.getAccessToken() && !!this.getCurrentUser();
  }

  /**
   * Get current user's email
   * @returns {string|null}
   */
  getCurrentUserEmail() {
    const user = this.getCurrentUser();
    return user?.email || null;
  }

  /**
   * Check if token is likely expired (client-side check)
   * @returns {boolean}
   */
  isTokenLikelyExpired() {
    const token = this.getAccessToken();
    if (!token) return true;

    try {
      // Decode JWT payload (without verification - just for expiry check)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Math.floor(Date.now() / 1000);
      return payload.exp < now;
    } catch {
      return true; // If we can't decode, assume expired
    }
  }
}

export const authClient = new AuthClient();
export default authClient;