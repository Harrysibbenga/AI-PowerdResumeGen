import axios from "axios";
import { API_BASE_URL } from "@/utils/api";
import { getFirebaseAuth } from "@/utils/firebase";

class ResumeClient {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api/v1/resume`
    });
  }

  getAuth() {
    return getFirebaseAuth();
  }

  async generateResume(resumeData) {
    const auth = this.getAuth();
    const user = auth.currentUser;
    if (!user) throw new Error("User not authenticated");

    const idToken = await user.getIdToken();
    const res = await this.api.post("/", resumeData, {
      headers: {
        Authorization: `Bearer ${idToken}`,
        "Content-Type": "application/json"
      }
    });

    return res.data;
  }

  async getResume(id) {
    const auth = this.getAuth();
    const user = auth.currentUser;
    if (!user) throw new Error("User not authenticated");

    const idToken = await user.getIdToken();
    const res = await this.api.get(`/${id}`, {
      headers: {
        Authorization: `Bearer ${idToken}`
      }
    });

    return res.data;
  }

  async deleteResume(id) {
    const auth = this.getAuth();
    const user = auth.currentUser;
    if (!user) throw new Error("User not authenticated");

    const idToken = await user.getIdToken();
    const res = await this.api.delete(`/${id}`, {
      headers: {
        Authorization: `Bearer ${idToken}`
      }
    });

    return res.data;
  }

  async listResumes() {
    const auth = this.getAuth();
    const user = auth.currentUser;
    if (!user) throw new Error("User not authenticated");

    const idToken = await user.getIdToken();
    const res = await this.api.get("/", {
      headers: {
        Authorization: `Bearer ${idToken}`
      }
    });

    return res.data;
  }
}

export const resumeClient = new ResumeClient();
export default resumeClient;
