import { getAuth, signInWithEmailAndPassword, signOut } from "firebase/auth";
import { initFirebase } from "@/utils/firebase";
import axios from "axios";

class AuthClient {
  constructor() {
    this.auth = null;
    this.api = axios.create({
      baseURL: "/api/v1/auth"
    });
  }

  async init() {
    if (!this.auth) {
      const firebaseApp = initFirebase();
      this.auth = getAuth(firebaseApp);
    }
  }

  async login(email, password, rememberMe = false) {
    await this.init();

    const userCredential = await signInWithEmailAndPassword(this.auth, email, password);
    const idToken = await userCredential.user.getIdToken();

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
  }

  async loginWith2FA(idToken, twoFactorCode, rememberMe = false) {
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
  }

  async refreshToken(refreshToken) {
    const res = await this.api.post("/refresh", {
      refresh_token: refreshToken
    });

    this._storeTokens(res.data);
    return res.data;
  }

  async logoutAllDevices() {
    await this.api.post("/logout/all", {}, {
      headers: {
        Authorization: `Bearer ${this.getAccessToken()}`
      }
    });

    await this.init();
    await signOut(this.auth);
    this._clearTokens();
  }

  getCurrentUser() {
    return this.auth?.currentUser ?? null;
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
