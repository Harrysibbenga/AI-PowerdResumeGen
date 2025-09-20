<template>
  <div class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow bg-gray-50">
    <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start mb-3">
      <div class="flex-1">
        <h3 class="text-xl font-bold text-gray-900">{{ experience.job_title || experience.title }}</h3>
        <p class="text-lg text-primary-600 font-semibold">
          {{ experience.company_name || experience.company }}
        </p>
        <p v-if="experience.location" class="text-gray-500">{{ experience.location }}</p>
      </div>
      <div class="text-sm text-gray-500 mt-2 lg:mt-0 lg:text-right">
        <p class="font-medium">
          {{ formatEmploymentPeriod(experience.employment_period || experience.startDate, experience.endDate, experience.current) }}
        </p>
      </div>
    </div>

    <!-- Key Achievements -->
    <div v-if="experience.key_achievements?.length || experience.highlights?.length" class="mt-4">
      <ul class="space-y-2">
        <li
          v-for="(achievement, achIndex) in (experience.key_achievements || experience.highlights)"
          :key="`achievement-${achIndex}`"
          class="flex items-start"
        >
          <span class="text-primary-500 mr-3 mt-1.5 flex-shrink-0">•</span>
          <span class="text-gray-700 leading-relaxed">{{ achievement }}</span>
        </li>
      </ul>
    </div>

    <!-- Description fallback -->
    <div v-else-if="experience.description" class="mt-4">
      <p class="text-gray-700 leading-relaxed">{{ experience.description }}</p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  experience: {
    type: Object,
    required: true,
  }
});

const formatEmploymentPeriod = (period, endDate, isCurrent = false) => {
  if (period && period.includes(" - ")) {
    return period;
  }
  
  if (period && endDate) {
    return `${formatDate(period)} - ${isCurrent ? "Present" : formatDate(endDate)}`;
  }
  
  return period || "N/A";
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  try {
    if (typeof dateString === "number") {
      return dateString.toString();
    }

    if (dateString.includes("/")) {
      const [month, year] = dateString.split("/");
      const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      return `${monthNames[parseInt(month) - 1]} ${year}`;
    }

    if (dateString.includes("-")) {
      const [year, month] = dateString.split("-");
      const date = new Date(year, month - 1);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
      });
    }

    return dateString;
  } catch {
    return dateString;
  }
};
</script>