<template>
  <div class="bg-gray-50 p-6 rounded-md">
    <h2 class="text-xl font-semibold mb-4">Resume Focus</h2>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Industry</label>
      <select
        v-model="industry"
        class="w-full px-3 py-2 border border-gray-300 rounded-md"
        @change="handleChange"
        required
      >
        <option value="">Select an industry</option>
        <option
          v-for="industryOption in industries"
          :key="industryOption.id"
          :value="industryOption.id"
        >
          {{ industryOption.name }}
        </option>
      </select>
      <p v-if="selectedIndustry" class="mt-2 text-sm text-gray-600">
        {{ selectedIndustry.description }}
      </p>
    </div>
  </div>
</template>

<script>
import { INDUSTRIES, getIndustryById } from "@/utils/industries.js";

export default {
  name: "IndustrySelector",
  props: {
    modelValue: { type: String, required: true },
  },
  emits: ["update:modelValue"],
  data() {
    return {
      industries: INDUSTRIES,
    };
  },
  computed: {
    industry: {
      get() {
        return this.modelValue;
      },
      set(val) {
        this.$emit("update:modelValue", val);
      },
    },
    selectedIndustry() {
      return this.industry ? getIndustryById(this.industry) : null;
    },
  },
  methods: {
    handleChange() {
      this.$emit("industryChanged", this.industry);
    },
  },
};
</script>
