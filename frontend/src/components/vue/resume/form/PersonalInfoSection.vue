<template>
  <div class="bg-gray-50 p-6 rounded-md">
    <h2 class="text-xl font-semibold mb-4">Personal Information</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
        <input
          v-model="localForm.fullName"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md"
          required
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
        <input
          v-model="localForm.email"
          type="email"
          class="w-full px-3 py-2 border border-gray-300 rounded-md"
          required
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
        <input
          v-model="localForm.phone"
          type="tel"
          class="w-full px-3 py-2 border border-gray-300 rounded-md"
          required
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
        <input
          v-model="localForm.location"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md"
          required
        />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1"
          >LinkedIn (optional)</label
        >
        <input
          v-model="localForm.linkedin"
          type="url"
          class="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PersonalInfoSection",
  props: {
    modelValue: { type: Object, required: true },
  },
  computed: {
    localForm: {
      get() {
        return this.modelValue;
      },
      set(val) {
        this.$emit("update:modelValue", val);
      },
    },
  },
};
</script>
