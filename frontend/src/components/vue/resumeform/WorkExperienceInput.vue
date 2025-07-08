<template>
  <div class="bg-gray-50 p-6 rounded-md">
    <h2 class="text-xl font-semibold mb-4">Work Experience</h2>
    <div class="space-y-6">
      <div
        v-for="(job, index) in modelValue"
        :key="index"
        class="p-4 border border-gray-200 rounded-md"
      >
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-medium">Experience #{{ index + 1 }}</h3>
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
            <label class="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
            <input
              v-model="job.title"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Company</label>
            <input
              v-model="job.company"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <input
              v-model="job.location"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >Start Date</label
              >
              <input
                v-model="job.startDate"
                type="month"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                v-model="job.endDate"
                type="month"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Present"
              />
            </div>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Description</label
            >
            <textarea
              v-model="job.description"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="Describe your responsibilities and achievements"
            ></textarea>
          </div>
        </div>
      </div>
    </div>
    <button type="button" @click="add" class="mt-4 text-blue-600 hover:text-blue-800">
      + Add Work Experience
    </button>
  </div>
</template>

<script>
export default {
  name: "WorkExperienceInput",
  props: {
    modelValue: { type: Array, required: true },
  },
  emits: ["update:modelValue"],
  methods: {
    add() {
      this.modelValue.push({
        title: "",
        company: "",
        location: "",
        startDate: "",
        endDate: "",
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
