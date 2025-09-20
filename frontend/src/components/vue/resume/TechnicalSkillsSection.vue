<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <div
      v-for="(skillList, category) in skills"
      :key="category"
      class="border border-gray-200 rounded-lg p-4 bg-gray-50"
    >
      <h3 class="font-semibold text-gray-900 mb-3 capitalize">
        {{ formatSkillCategory(category) }}
      </h3>
      <div class="flex flex-wrap gap-2">
        <SkillPill
          v-for="(skill, skillIndex) in skillList"
          :key="`skill-${category}-${skillIndex}`"
          :label="skill"
          variant="gray"
          size="sm"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import SkillPill from '../ui/SkillPill.vue';

const props = defineProps({
  skills: {
    type: Object,
    required: true,
  }
});

const formatSkillCategory = (category) => {
  return category.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase());
};
</script>