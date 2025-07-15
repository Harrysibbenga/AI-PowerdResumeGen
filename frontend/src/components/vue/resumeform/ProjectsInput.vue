<template>
  <div class="bg-gray-50 p-6 rounded-md">
    <h2 class="text-xl font-semibold mb-4">Projects</h2>
    <div class="space-y-6">
      <div
        v-for="(project, index) in modelValue"
        :key="index"
        class="p-4 border border-gray-200 rounded-md"
      >
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-medium">Project #{{ index + 1 }}</h3>
          <button
            v-if="modelValue.length > 1"
            type="button"
            @click="remove(index)"
            class="text-red-600 hover:text-red-800"
          >
            Remove
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Project Title</label
            >
            <input
              v-model="project.title"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="e.g., E-commerce Web Application"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Project URL (optional)</label
            >
            <input
              v-model="project.url"
              type="url"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="https://github.com/user/project"
            />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >Start Date</label
              >
              <input
                v-model="project.startDate"
                type="month"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                v-model="project.endDate"
                type="month"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Present"
              />
            </div>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Technologies Used</label
            >
            <div class="flex flex-wrap gap-2 mb-2">
              <span
                v-for="(tech, techIndex) in project.technologies"
                :key="techIndex"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {{ tech }}
                <button
                  type="button"
                  @click="removeTechnology(index, techIndex)"
                  class="ml-1 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            </div>
            <div class="flex gap-2">
              <input
                v-model="newTech[index]"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Add technology (e.g., React, Python, AWS)"
                @keyup.enter="addTechnology(index)"
              />
              <button
                type="button"
                @click="addTechnology(index)"
                class="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Add
              </button>
            </div>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Project Description</label
            >
            <textarea
              v-model="project.description"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="Describe the project, your role, and key achievements"
              required
            ></textarea>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Key Highlights</label
            >
            <div class="space-y-2">
              <div
                v-for="(highlight, highlightIndex) in project.highlights"
                :key="highlightIndex"
                class="flex items-center"
              >
                <input
                  v-model="project.highlights[highlightIndex]"
                  type="text"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Key achievement or feature"
                />
                <button
                  type="button"
                  @click="removeHighlight(index, highlightIndex)"
                  class="ml-2 text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              </div>
            </div>
            <button
              type="button"
              @click="addHighlight(index)"
              class="mt-2 text-blue-600 hover:text-blue-800"
            >
              + Add Highlight
            </button>
          </div>
        </div>
      </div>
    </div>
    <button type="button" @click="add" class="mt-4 text-blue-600 hover:text-blue-800">
      + Add Project
    </button>
  </div>
</template>

<script>
export default {
  name: "ProjectsInput",
  props: {
    modelValue: { type: Array, required: true },
  },
  emits: ["update:modelValue"],
  data() {
    return {
      newTech: {}, // Track new technology input for each project
    };
  },
  methods: {
    add() {
      this.modelValue.push({
        title: "",
        description: "",
        technologies: [],
        url: "",
        startDate: "",
        endDate: "",
        highlights: [""],
      });
      this.$emit("update:modelValue", [...this.modelValue]);
    },
    remove(index) {
      if (this.modelValue.length > 1) {
        this.modelValue.splice(index, 1);
        delete this.newTech[index];
        this.$emit("update:modelValue", [...this.modelValue]);
      }
    },
    addTechnology(projectIndex) {
      const tech = this.newTech[projectIndex];
      if (
        tech &&
        tech.trim() &&
        !this.modelValue[projectIndex].technologies.includes(tech.trim())
      ) {
        this.modelValue[projectIndex].technologies.push(tech.trim());
        this.newTech[projectIndex] = "";
        this.$emit("update:modelValue", [...this.modelValue]);
      }
    },
    removeTechnology(projectIndex, techIndex) {
      this.modelValue[projectIndex].technologies.splice(techIndex, 1);
      this.$emit("update:modelValue", [...this.modelValue]);
    },
    addHighlight(projectIndex) {
      this.modelValue[projectIndex].highlights.push("");
      this.$emit("update:modelValue", [...this.modelValue]);
    },
    removeHighlight(projectIndex, highlightIndex) {
      this.modelValue[projectIndex].highlights.splice(highlightIndex, 1);
      if (this.modelValue[projectIndex].highlights.length === 0) {
        this.modelValue[projectIndex].highlights.push("");
      }
      this.$emit("update:modelValue", [...this.modelValue]);
    },
  },
};
</script>
