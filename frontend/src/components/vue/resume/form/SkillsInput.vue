<template>
  <div class="bg-gray-50 p-6 rounded-md">
    <h2 class="text-xl font-semibold mb-4">Skills</h2>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Top Skills</label>
      <div v-if="industry && suggestions.length" class="mb-3">
        <p class="text-sm text-gray-600 mb-2">Suggested skills for {{ industryName }}:</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="skill in suggestions"
            :key="skill"
            type="button"
            @click="addSkill(skill)"
            class="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-full hover:bg-blue-200"
          >
            + {{ skill }}
          </button>
        </div>
      </div>
      <div class="space-y-2">
        <div v-for="(skill, index) in modelValue" :key="index" class="flex items-center">
          <input
            v-model="modelValue[index]"
            type="text"
            class="flex-1 px-3 py-2 border border-gray-300 rounded-md"
          />
          <button
            type="button"
            @click="removeSkill(index)"
            class="ml-2 text-red-600 hover:text-red-800"
          >
            Remove
          </button>
        </div>
      </div>
      <button
        type="button"
        @click="modelValue.push('')"
        class="mt-2 text-blue-600 hover:text-blue-800"
      >
        + Add Skill
      </button>
    </div>
  </div>
</template>

<script>
import { getSkillSuggestions, getIndustryById } from "@/utils/industries.js";

export default {
  name: "SkillsInput",
  props: {
    modelValue: { type: Array, required: true },
    industry: { type: String, required: true },
  },
  emits: ["update:modelValue"],
  computed: {
    suggestions() {
      return this.industry ? getSkillSuggestions(this.industry) : [];
    },
    industryName() {
      const industry = getIndustryById(this.industry);
      return industry?.name || "";
    },
  },
  methods: {
    addSkill(skill) {
      if (!this.modelValue.includes(skill)) {
        if (this.modelValue.length === 1 && this.modelValue[0] === "") {
          this.modelValue[0] = skill;
        } else {
          this.modelValue.push(skill);
        }
        this.$emit("update:modelValue", [...this.modelValue]);
      }
    },
    removeSkill(index) {
      this.modelValue.splice(index, 1);
      if (this.modelValue.length === 0) this.modelValue.push("");
      this.$emit("update:modelValue", [...this.modelValue]);
    },
  },
};
</script>
