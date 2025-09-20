<template>
  <div class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow bg-gray-50">
    <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start">
      <div class="flex-1">
        <h3 class="text-lg font-bold text-gray-900">{{ education.degree }}</h3>
        <p class="text-primary-600 font-semibold">{{ education.institution || education.school }}</p>
        <p v-if="education.location" class="text-gray-500">{{ education.location }}</p>
        <p v-if="education.gpa" class="text-sm text-gray-600 mt-1">
          GPA: {{ education.gpa }}
        </p>
        <p v-if="education.relevant_details || education.description" class="text-sm text-gray-600 mt-1">
          {{ education.relevant_details || education.description }}
        </p>
      </div>
      <div class="text-sm text-gray-500 mt-2 lg:mt-0 lg:text-right">
        <p class="font-medium">{{ formatEducationDate(education) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  education: {
    type: Object,
    required: true,
  }
});

const formatEducationDate = (edu) => {
  if (edu.graduation_date || edu.graduationDate) {
    return formatDate(edu.graduation_date || edu.graduationDate);
  }

  if (edu.endYear) {
    return edu.startYear ? `${edu.startYear} - ${edu.endYear}` : edu.endYear.toString();
  }

  return edu.startYear ? edu.startYear.toString() : "N/A";
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