<template>
  <div class="bg-white p-6 rounded-lg border border-gray-200">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">Projects</h3>
      <button
        type="button"
        @click="startAddingProject"
        class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        + Add Project
      </button>
    </div>

    <!-- Display existing projects -->
    <div v-if="projects.length > 0" class="space-y-6 mb-6">
      <div
        v-for="(project, index) in projects"
        :key="index"
        class="bg-gray-50 p-6 border border-gray-200 rounded-lg"
      >
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            {{ project.title || `Project #${index + 1}` }}
          </h3>
          <button
            type="button"
            @click="removeProject(index)"
            class="text-red-600 hover:text-red-800 text-sm font-medium"
          >
            Remove Project
          </button>
        </div>

        <!-- Project summary display -->
        <div class="space-y-3">
          <div v-if="project.description" class="text-sm text-gray-600">
            {{ project.description.substring(0, 150)
            }}{{ project.description.length > 150 ? "..." : "" }}
          </div>

          <div class="flex flex-wrap items-center gap-4 text-sm text-gray-500">
            <span v-if="project.startDate || project.endDate">
              📅 {{ formatDateRange(project.startDate, project.endDate) }}
            </span>
            <span v-if="project.url" class="flex items-center">
              🔗
              <a
                :href="project.url"
                target="_blank"
                class="text-blue-600 hover:text-blue-800 ml-1"
                >View Project</a
              >
            </span>
          </div>

          <div
            v-if="project.technologies && project.technologies.length > 0"
            class="flex flex-wrap gap-1"
          >
            <span
              v-for="tech in project.technologies.slice(0, 5)"
              :key="tech"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              {{ tech }}
            </span>
            <span v-if="project.technologies.length > 5" class="text-xs text-gray-500">
              +{{ project.technologies.length - 5 }} more
            </span>
          </div>
        </div>

        <!-- Edit button -->
        <button
          type="button"
          @click="editProject(index)"
          class="mt-3 text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Edit Project
        </button>
      </div>
    </div>

    <!-- Project form (for adding or editing) -->
    <div
      v-if="showProjectForm"
      class="bg-white p-6 border border-gray-200 rounded-lg shadow-sm space-y-6"
    >
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-medium text-gray-900">
          {{ editingIndex !== null ? "Edit Project" : "Add New Project" }}
        </h3>
        <button
          type="button"
          @click="cancelProjectForm"
          class="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Project Title*
          </label>
          <input
            v-model="currentProject.title"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., E-commerce Web Application"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Project URL (optional)
          </label>
          <input
            v-model="currentProject.url"
            type="url"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="https://github.com/user/project"
          />
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              v-model="currentProject.startDate"
              type="month"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"> End Date </label>
            <input
              v-model="currentProject.endDate"
              type="month"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Leave empty if ongoing"
            />
          </div>
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Technologies Used
          </label>
          <div class="flex flex-wrap gap-2 mb-2">
            <span
              v-for="(tech, techIndex) in currentProject.technologies"
              :key="techIndex"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              {{ tech }}
              <button
                type="button"
                @click="removeTechnology(techIndex)"
                class="ml-1 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          </div>
          <div class="flex gap-2">
            <input
              v-model="newTech"
              type="text"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add technology (e.g., React, Python, AWS)"
              @keyup.enter="addTechnology"
            />
            <button
              type="button"
              @click="addTechnology"
              :disabled="!newTech.trim()"
              class="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Add
            </button>
          </div>
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Project Description*
          </label>
          <textarea
            v-model="currentProject.description"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Describe the project, your role, and key achievements"
            required
          ></textarea>
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Key Highlights
          </label>
          <div class="space-y-2">
            <div
              v-for="(highlight, highlightIndex) in currentProject.highlights"
              :key="highlightIndex"
              class="flex items-center gap-2"
            >
              <input
                v-model="currentProject.highlights[highlightIndex]"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Key achievement or feature"
              />
              <button
                type="button"
                @click="removeHighlight(highlightIndex)"
                class="text-red-600 hover:text-red-800 px-2"
              >
                Remove
              </button>
            </div>
          </div>
          <button
            type="button"
            @click="addHighlight"
            class="mt-2 text-blue-600 hover:text-blue-800 text-sm"
          >
            + Add Highlight
          </button>
        </div>
      </div>

      <!-- Form actions -->
      <div class="flex justify-end space-x-3 pt-4 border-t">
        <button
          type="button"
          @click="cancelProjectForm"
          class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="saveProject"
          :disabled="!currentProject.title.trim() || !currentProject.description.trim()"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {{ editingIndex !== null ? "Update Project" : "Add Project" }}
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
      <i class="pi pi-folder text-4xl text-gray-400 mb-2"></i>
      <p class="text-gray-600 font-medium">No projects added yet</p>
      <p class="text-gray-500 text-sm mt-1">Click "Add Project" to showcase your work</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";

const props = defineProps({
  modelValue: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(['update:modelValue', 'change']);

// Debug logging
onMounted(() => {
  console.log('ProjectsInput mounted with modelValue:', props.modelValue);
  console.log('Projects array type:', typeof props.modelValue, 'isArray:', Array.isArray(props.modelValue));
  if (Array.isArray(props.modelValue)) {
    console.log('Projects count:', props.modelValue.length);
    props.modelValue.forEach((project, index) => {
      console.log(`Project ${index}:`, project.title || 'Untitled');
    });
  }
});

// Safe access to projects array
const projects = computed(() => {
  console.log('ProjectsInput - modelValue:', props.modelValue);
  if (!Array.isArray(props.modelValue)) {
    console.warn('ProjectsInput - modelValue is not an array:', typeof props.modelValue, props.modelValue);
    return [];
  }
  return props.modelValue;
});

// State
const showProjectForm = ref(false);
const editingIndex = ref(null);
const newTech = ref("");

// Current project being edited/added
const currentProject = reactive({
  title: "",
  description: "",
  technologies: [],
  url: "",
  startDate: "",
  endDate: "",
  highlights: [""],
});

// Update projects array
const updateProjects = (newProjects) => {
  console.log('ProjectsInput - updating projects:', newProjects);
  emit('update:modelValue', newProjects);
  emit('change');
};

// Start adding a new project
const startAddingProject = () => {
  resetCurrentProject();
  editingIndex.value = null;
  showProjectForm.value = true;
};

// Edit existing project
const editProject = (index) => {
  const project = projects.value[index];

  // Copy project data to currentProject
  currentProject.title = project.title || "";
  currentProject.description = project.description || "";
  currentProject.technologies = [...(project.technologies || [])];
  currentProject.url = project.url || "";
  currentProject.startDate = project.startDate || "";
  currentProject.endDate = project.endDate || "";
  currentProject.highlights = [...(project.highlights || [""])];

  editingIndex.value = index;
  showProjectForm.value = true;
};

// Save project (add or update)
const saveProject = () => {
  if (!currentProject.title.trim() || !currentProject.description.trim()) {
    return;
  }

  const projectData = {
    title: currentProject.title.trim(),
    description: currentProject.description.trim(),
    technologies: [...currentProject.technologies],
    url: currentProject.url.trim(),
    startDate: currentProject.startDate,
    endDate: currentProject.endDate,
    highlights: currentProject.highlights.filter((h) => h.trim()),
  };

  const updatedProjects = [...projects.value];
  
  if (editingIndex.value !== null) {
    // Update existing project
    updatedProjects[editingIndex.value] = projectData;
  } else {
    // Add new project
    updatedProjects.push(projectData);
  }

  updateProjects(updatedProjects);
  cancelProjectForm();
};

// Cancel form
const cancelProjectForm = () => {
  showProjectForm.value = false;
  editingIndex.value = null;
  resetCurrentProject();
};

// Reset current project form
const resetCurrentProject = () => {
  currentProject.title = "";
  currentProject.description = "";
  currentProject.technologies = [];
  currentProject.url = "";
  currentProject.startDate = "";
  currentProject.endDate = "";
  currentProject.highlights = [""];
  newTech.value = "";
};

// Remove project
const removeProject = (index) => {
  const updatedProjects = [...projects.value];
  updatedProjects.splice(index, 1);
  updateProjects(updatedProjects);
};

// Technology management
const addTechnology = () => {
  const tech = newTech.value.trim();
  if (tech && !currentProject.technologies.includes(tech)) {
    currentProject.technologies.push(tech);
    newTech.value = "";
  }
};

const removeTechnology = (index) => {
  currentProject.technologies.splice(index, 1);
};

// Highlight management
const addHighlight = () => {
  currentProject.highlights.push("");
};

const removeHighlight = (index) => {
  currentProject.highlights.splice(index, 1);
  if (currentProject.highlights.length === 0) {
    currentProject.highlights.push("");
  }
};

// Format date range for display
const formatDateRange = (startDate, endDate) => {
  if (!startDate && !endDate) return "";

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    const [year, month] = dateStr.split("-");
    const monthNames = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];
    return `${monthNames[parseInt(month) - 1]} ${year}`;
  };

  const start = startDate ? formatDate(startDate) : "";
  const end = endDate ? formatDate(endDate) : "Present";

  if (start && end) {
    return `${start} - ${end}`;
  } else if (start) {
    return `${start} - Present`;
  } else if (end && end !== "Present") {
    return `Until ${end}`;
  }
  return "";
};
</script>
