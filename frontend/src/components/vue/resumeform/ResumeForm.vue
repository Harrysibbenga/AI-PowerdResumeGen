<template>
  <form @submit.prevent="handleSubmit" class="space-y-8">
    <p v-if="error" class="text-red-600">{{ error }}</p>
    <div v-if="loading" class="text-center text-blue-600">Generating resume...</div>

    <PersonalInfoSection v-model="form" />
    <IndustrySelector v-model="form.industry" @industryChanged="handleIndustryChange" />
    <SkillsInput v-model="form.skills" :industry="form.industry" />
    <CertificationsInput v-model="form.certifications" :industry="form.industry" />
    <WorkExperienceInput v-model="form.workExperience" />
    <EducationInput v-model="form.education" />

    <div class="flex justify-center">
      <button
        type="submit"
        class="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
      >
        Generate Resume
      </button>
    </div>
  </form>
</template>

<script>
import PersonalInfoSection from "./PersonalInfoSection.vue";
import IndustrySelector from "./IndustrySelector.vue";
import SkillsInput from "./SkillsInput.vue";
import CertificationsInput from "./CertificationsInput.vue";
import WorkExperienceInput from "./WorkExperienceInput.vue";
import EducationInput from "./EducationInput.vue";
import { capitalize } from "@/utils/formatters.js";
import { getAuth } from "firebase/auth";
import { defaultForm } from "@/utils/defaultForm.js";
import { API_BASE_URL } from "@/utils/api";

export default {
  name: "ResumeForm",
  components: {
    PersonalInfoSection,
    IndustrySelector,
    SkillsInput,
    CertificationsInput,
    WorkExperienceInput,
    EducationInput,
  },
  data() {
    return {
      loading: false,
      error: "",
      form: JSON.parse(JSON.stringify(defaultForm)), // clone to avoid mutation
    };
  },
  // data() {
  //   return {
  //     loading: false,
  //     error: "",
  //     form: {
  //       fullName: "",
  //       email: "",
  //       phone: "",
  //       linkedin: "",
  //       location: "",
  //       industry: "",
  //       skills: [""],
  //       certifications: [""],
  //       workExperience: [
  //         {
  //           title: "",
  //           company: "",
  //           location: "",
  //           startDate: "",
  //           endDate: "",
  //           description: "",
  //         },
  //       ],
  //       education: [
  //         {
  //           degree: "",
  //           school: "",
  //           location: "",
  //           graduationDate: "",
  //           description: "",
  //         },
  //       ],
  //     },
  //   };
  // },
  methods: {
    handleIndustryChange() {},
    formatFormData() {
      this.form.fullName = capitalize(this.form.fullName);
      this.form.location = capitalize(this.form.location);
      this.form.skills = this.form.skills.filter((s) => s.trim());
      this.form.certifications = this.form.certifications.filter((c) => c.trim());
      this.form.workExperience.forEach((j) => {
        j.title = capitalize(j.title);
        j.company = capitalize(j.company);
        j.location = capitalize(j.location);
      });
      this.form.education.forEach((e) => {
        e.degree = capitalize(e.degree);
        e.school = capitalize(e.school);
        e.location = capitalize(e.location);
      });
    },
    async handleSubmit() {
      this.error = "";
      this.loading = true;
      try {
        this.formatFormData();
        const auth = getAuth();
        const user = auth.currentUser;
        if (!user) throw new Error("Login required");

        const idToken = await user.getIdToken();
        const profile = {
          name: this.form.fullName,
          email: this.form.email,
          phone: this.form.phone,
          linkedin: this.form.linkedin,
          experience: this.form.workExperience,
          education: this.form.education.map((edu) => ({
            degree: edu.degree,
            institution: edu.school,
            startYear: parseInt(edu.graduationDate?.split("-")[0]) || 2020,
            endYear: parseInt(edu.graduationDate?.split("-")[0]) || undefined,
          })),
          skills: this.form.skills,
          industry: this.form.industry,
        };

        const res = await fetch(`${API_BASE_URL}/api/v1/resumes`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${idToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ profile, tone: "professional" }),
        });

        if (!res.ok) throw new Error("Failed to generate resume");
        const data = await res.json();
        window.location.href = `/preview?id=${data.id}`;
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
