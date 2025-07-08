<template>
  <div>
    <h1 class="text-3xl font-bold mb-4 text-center">
      {{ name || "Loading..." }}
    </h1>
    <p class="text-gray-700 text-center mb-8">
      {{ summary || "No summary available." }}
    </p>

    <div class="space-y-8">
      <section v-if="experience.length">
        <h2 class="text-xl font-semibold mb-2">Experience</h2>
        <div
          v-for="(exp, i) in experience"
          :key="i"
          class="bg-gray-50 p-4 border border-gray-200 rounded-md"
        >
          <p class="font-semibold">{{ exp.title }} at {{ exp.company }}</p>
          <p class="text-sm text-gray-600">
            {{ exp.startDate }} - {{ exp.endDate || "Present" }}
          </p>
          <ul class="list-disc list-inside text-sm mt-2">
            <li v-for="(d, j) in exp.description" :key="j">{{ d }}</li>
          </ul>
        </div>
      </section>

      <section v-if="education.length">
        <h2 class="text-xl font-semibold mb-2">Education</h2>
        <div
          v-for="(edu, i) in education"
          :key="i"
          class="bg-gray-50 p-4 border border-gray-200 rounded-md"
        >
          <p class="font-semibold">{{ edu.degree }} - {{ edu.institution }}</p>
          <p class="text-sm text-gray-600">
            {{ edu.startYear }} - {{ edu.endYear || "Present" }}
          </p>
        </div>
      </section>

      <section v-if="Object.keys(skills).length">
        <h2 class="text-xl font-semibold mb-2">Skills</h2>
        <div v-for="(items, group) in skills" :key="group" class="mb-4">
          <p class="font-semibold mb-1">{{ group }}</p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(s, i) in items"
              :key="i"
              class="px-2 py-1 text-sm bg-blue-100 rounded-full"
            >
              {{ s }}
            </span>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { app } from "@/utils/firebase";

export default {
  data() {
    return {
      name: "",
      summary: "",
      experience: [],
      education: [],
      skills: {},
    };
  },
  async mounted() {
    const resumeId = new URLSearchParams(window.location.search).get("id");
    const auth = getAuth(app);

    onAuthStateChanged(auth, async (user) => {
      if (!user) return (window.location.href = "/login");

      try {
        const token = await user.getIdToken();
        const res = await fetch(
          `${import.meta.env.PUBLIC_API_URL}/api/v1/resumes/${resumeId}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        const data = await res.json();
        this.name = data.profile_data?.name || "Resume Preview";
        this.summary = data.ai_content?.summary || "";
        this.experience = data.ai_content?.experience || [];
        this.education = data.ai_content?.education || [];
        this.skills = data.ai_content?.skills || {};
      } catch (err) {
        this.name = "Failed to load resume";
        this.summary = err.message;
      }
    });
  },
};
</script>
