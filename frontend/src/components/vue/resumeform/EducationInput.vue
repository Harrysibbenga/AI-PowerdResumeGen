<template>
  <div class="bg-gray-50 p-6 rounded-md">
    <h2 class="text-xl font-semibold mb-4">Education</h2>
    <div class="space-y-6">
      <div
        v-for="(edu, index) in modelValue"
        :key="index"
        class="p-4 border border-gray-200 rounded-md"
      >
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-medium">Education #{{ index + 1 }}</h3>
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
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Degree</label>
            <input
              v-model="edu.degree"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">School</label>
            <input
              v-model="edu.school"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <input
              v-model="edu.location"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Graduation Date</label
            >
            <input
              v-model="edu.graduationDate"
              type="month"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Description</label
            >
            <textarea
              v-model="edu.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="Relevant coursework, honors, activities"
            ></textarea>
          </div>
        </div>
      </div>
    </div>
    <button type="button" @click="add" class="mt-4 text-blue-600 hover:text-blue-800">
      + Add Education
    </button>
  </div>
</template>

<script>
export default {
  name: "EducationInput",
  props: {
    modelValue: { type: Array, required: true },
  },
  emits: ["update:modelValue"],
  methods: {
    add() {
      this.modelValue.push({
        degree: "",
        school: "",
        location: "",
        graduationDate: "",
        description: "",
      });
      this.$emit("update:modelValue", [...this.modelValue]);
    },
    remove(index) {
      if (this.modelValue.length > 1) {
        this.modelValue.splice(index, 1);
        this.$emit("update:modelValue", [...this.modelValue]);
      }
    },
  },
};
</script>
