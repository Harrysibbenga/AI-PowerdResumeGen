import { signInWithEmailAndPassword, signOut } from "firebase/auth";
import { getFirebaseAuth } from "@/utils/firebase";
import { API_BASE_URL } from "../utils/api";
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
}

export const authClient = new AuthClient();