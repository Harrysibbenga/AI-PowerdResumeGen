<template>
  <header class="bg-gradient-to-r from-gray-50 to-white p-8 border-b border-gray-200">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900 mb-3">
        {{ personalInfo.name }}
      </h1>

      <!-- Contact Information -->
      <div class="flex flex-wrap justify-center items-center gap-4 text-gray-600 mb-4">
        <span v-if="personalInfo.email" class="flex items-center">
          <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path
              d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"
            ></path>
            <path
              d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"
            ></path>
          </svg>
          {{ personalInfo.email }}
        </span>
        <span v-if="personalInfo.phone" class="flex items-center">
          <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path
              d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"
            ></path>
          </svg>
          {{ personalInfo.phone }}
        </span>
        <span v-if="personalInfo.location" class="flex items-center">
          <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
              clip-rule="evenodd"
            ></path>
          </svg>
          {{ personalInfo.location }}
        </span>
        <span v-if="personalInfo.linkedin" class="flex items-center">
          <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z"
              clip-rule="evenodd"
            ></path>
          </svg>
          <a
            :href="personalInfo.linkedin"
            target="_blank"
            class="text-blue-600 hover:text-blue-800"
            >LinkedIn</a
          >
        </span>
      </div>
    </div>
  </header>
</template>

<script setup>
const props = defineProps({
  personalInfo: {
    type: Object,
    required: true,
  }
});
</script>