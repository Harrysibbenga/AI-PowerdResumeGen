<template>
  <div class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow bg-gray-50">
    <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start mb-3">
      <h3 class="text-lg font-bold text-gray-900">
        {{ project.project_name || project.name || project.title }}
      </h3>
      <a
        v-if="project.url"
        :href="project.url"
        target="_blank"
        class="text-primary-600 hover:text-primary-800 text-sm font-medium"
      >
        View Project →
      </a>
    </div>

    <p v-if="project.description" class="text-gray-700 mb-3 leading-relaxed">
      {{ project.description }}
    </p>

    <!-- Technologies -->
    <div v-if="project.key_technologies?.length || project.technologies?.length" class="mb-3">
      <p class="text-sm font-medium text-gray-700 mb-2">Technologies:</p>
      <div class="flex flex-wrap gap-1">
        <SkillPill
          v-for="tech in (project.key_technologies || project.technologies)"
          :key="tech"
          :label="tech"
          variant="blue"
          size="sm"
        />
      </div>
    </div>

    <!-- Measurable Outcomes -->
    <div v-if="project.measurable_outcome || project.outcomes" class="text-sm text-gray-600">
      <strong>Outcomes:</strong> {{ project.measurable_outcome || project.outcomes }}
    </div>
  </div>
</template>

<script setup>
import SkillPill from '../ui/SkillPill.vue';

const props = defineProps({
  project: {
    type: Object,
    required: true,
  }
});
</script>