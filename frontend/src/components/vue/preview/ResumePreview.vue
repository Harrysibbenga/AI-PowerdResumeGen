<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-6xl mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button
              @click="goBack"
              class="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
                  clip-rule="evenodd"
                ></path>
              </svg>
              Back to Dashboard
            </button>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center space-x-3">
            <button
              @click="regenerateContent"
              :disabled="regenerating"
              class="flex items-center px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg
                v-if="!regenerating"
                class="w-4 h-4 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                  clip-rule="evenodd"
                ></path>
              </svg>
              <svg
                v-else
                class="animate-spin w-4 h-4 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                ></path>
              </svg>
              {{ regenerating ? "Regenerating..." : "Regenerate" }}
            </button>

            <button
              @click="editResume"
              class="flex items-center px-3 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"
                ></path>
              </svg>
              Edit Resume
            </button>

            <!-- Export Dropdown -->
            <div class="relative" ref="exportDropdown">
              <button
                @click="toggleExportMenu"
                :disabled="exporting"
                class="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-primary-400 transition-colors"
              >
                <svg
                  v-if="!exporting"
                  class="w-4 h-4 mr-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  ></path>
                </svg>
                <svg
                  v-else
                  class="animate-spin w-4 h-4 mr-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                  ></path>
                </svg>
                {{ exporting ? "Exporting..." : "Export" }}
                <svg
                  v-if="!exporting"
                  class="w-4 h-4 ml-1"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  ></path>
                </svg>
              </button>

              <!-- Export Menu -->
              <div
                v-if="showExportMenu"
                class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 z-10"
              >
                <div class="py-1">
                  <button
                    @click="exportResume('pdf')"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <svg
                      class="w-4 h-4 inline mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                        clip-rule="evenodd"
                      ></path>
                    </svg>
                    Export as PDF
                  </button>
                  <button
                    @click="exportResume('docx')"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <svg
                      class="w-4 h-4 inline mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm3 5a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3z"
                        clip-rule="evenodd"
                      ></path>
                    </svg>
                    Export as Word
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Resume Metadata -->
        <div
          v-if="resumeMetadata"
          class="mt-3 flex items-center space-x-6 text-sm text-gray-500"
        >
          <div class="text-sm text-gray-500">
            <span>Title: </span>
            <span v-if="resumeMetadata" class="font-medium text-gray-700">{{
              resumeMetadata.title
            }}</span>
          </div>
          <span v-if="resumeMetadata.target_job_title" class="flex items-center">
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z"
                clip-rule="evenodd"
              ></path>
            </svg>
            {{ resumeMetadata.target_job_title }}
            <span v-if="resumeMetadata.target_job_role" class="ml-1"
              >({{ resumeMetadata.target_job_role }})</span
            >
          </span>
          <span v-if="resumeMetadata.industry" class="flex items-center">
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                clip-rule="evenodd"
              ></path>
            </svg>
            {{ formatIndustry(resumeMetadata.industry) }}
          </span>
          <span v-if="resumeMetadata.template_id" class="flex items-center">
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                clip-rule="evenodd"
              ></path>
            </svg>
            {{ formatTemplate(resumeMetadata.template_id) }} Template
          </span>
          <span v-if="resumeMetadata.word_count" class="flex items-center">
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clip-rule="evenodd"
              ></path>
            </svg>
            {{ resumeMetadata.word_count.toLocaleString() }} words
          </span>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto p-6">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"
        ></div>
        <p class="text-gray-600">Loading resume...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <div class="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
          <svg
            class="w-12 h-12 text-red-400 mx-auto mb-4"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clip-rule="evenodd"
            ></path>
          </svg>
          <h2 class="text-xl font-semibold text-red-800 mb-2">Failed to Load Resume</h2>
          <p class="text-red-600 mb-4">{{ error }}</p>
          <button
            @click="loadResume"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Resume Content -->
      <div v-else class="bg-white shadow-lg rounded-lg overflow-hidden">
        <!-- Header Section -->
        <header
          class="bg-gradient-to-r from-gray-50 to-white p-8 border-b border-gray-200"
        >
          <div class="text-center">
            <h1 class="text-4xl font-bold text-gray-900 mb-3">
              {{
                resumeData.sections?.personal_info?.name ||
                resumeData.profile?.name ||
                "Resume Preview"
              }}
            </h1>

            <!-- Contact Information -->
            <div
              class="flex flex-wrap justify-center items-center gap-4 text-gray-600 mb-4"
            >
              <span v-if="getContactInfo().email" class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"
                  ></path>
                  <path
                    d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"
                  ></path>
                </svg>
                {{ getContactInfo().email }}
              </span>
              <span v-if="getContactInfo().phone" class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"
                  ></path>
                </svg>
                {{ getContactInfo().phone }}
              </span>
              <span v-if="getContactInfo().location" class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
                    clip-rule="evenodd"
                  ></path>
                </svg>
                {{ getContactInfo().location }}
              </span>
              <span v-if="getContactInfo().linkedin" class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z"
                    clip-rule="evenodd"
                  ></path>
                </svg>
                <a
                  :href="getContactInfo().linkedin"
                  target="_blank"
                  class="text-blue-600 hover:text-blue-800"
                  >LinkedIn</a
                >
              </span>
            </div>
          </div>
        </header>

        <div class="p-8">
          <!-- Professional Summary -->
          <section v-if="resumeData.sections?.professional_summary" class="mb-8">
            <h2 class="section-header">Professional Summary</h2>
            <div class="prose text-gray-700 leading-relaxed">
              <p>{{ resumeData.sections.professional_summary }}</p>
            </div>
          </section>

          <!-- Core Competencies -->
          <section v-if="resumeData.sections?.core_competencies?.length" class="mb-8">
            <h2 class="section-header">Core Competencies</h2>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(skill, index) in resumeData.sections.core_competencies"
                :key="`competency-${index}`"
                class="inline-block px-3 py-1.5 bg-primary-100 text-primary-800 rounded-full text-sm font-medium"
              >
                {{ skill }}
              </span>
            </div>
          </section>

          <!-- Professional Experience -->
          <section v-if="resumeData.sections?.experience?.length" class="mb-8">
            <h2 class="section-header">Professional Experience</h2>
            <div class="space-y-6">
              <div
                v-for="(exp, index) in resumeData.sections.experience"
                :key="`exp-${index}`"
                class="experience-card"
              >
                <div
                  class="flex flex-col lg:flex-row lg:justify-between lg:items-start mb-3"
                >
                  <div class="flex-1">
                    <h3 class="text-xl font-bold text-gray-900">{{ exp.title }}</h3>
                    <p class="text-lg text-primary-600 font-semibold">
                      {{ exp.company }}
                    </p>
                    <p v-if="exp.location" class="text-gray-500">{{ exp.location }}</p>
                  </div>
                  <div class="text-sm text-gray-500 mt-2 lg:mt-0 lg:text-right">
                    <p class="font-medium">
                      {{ formatDateRange(exp.startDate, exp.endDate, exp.current) }}
                    </p>
                  </div>
                </div>

                <!-- Achievements -->
                <div v-if="exp.achievements?.length" class="mt-4">
                  <ul class="space-y-2">
                    <li
                      v-for="(achievement, achIndex) in exp.achievements"
                      :key="`achievement-${index}-${achIndex}`"
                      class="flex items-start"
                    >
                      <span class="text-primary-500 mr-3 mt-1.5 flex-shrink-0">•</span>
                      <span class="text-gray-700 leading-relaxed">{{ achievement }}</span>
                    </li>
                  </ul>
                </div>

                <!-- Legacy description support -->
                <div v-else-if="exp.description" class="mt-4">
                  <p class="text-gray-700 leading-relaxed">{{ exp.description }}</p>
                </div>
              </div>
            </div>
          </section>

          <!-- Technical Skills -->
          <section v-if="resumeData.sections?.technical_skills" class="mb-8">
            <h2 class="section-header">Technical Skills</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div
                v-for="(skillList, category) in resumeData.sections.technical_skills"
                :key="category"
                class="skill-category"
              >
                <h3 class="font-semibold text-gray-900 mb-3 capitalize">
                  {{ formatSkillCategory(category) }}
                </h3>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(skill, skillIndex) in skillList"
                    :key="`skill-${category}-${skillIndex}`"
                    class="inline-block px-2.5 py-1 text-sm bg-gray-100 text-gray-800 rounded-md"
                  >
                    {{ skill }}
                  </span>
                </div>
              </div>
            </div>
          </section>

          <!-- Education -->
          <section v-if="resumeData.sections?.education?.length" class="mb-8">
            <h2 class="section-header">Education</h2>
            <div class="space-y-4">
              <div
                v-for="(edu, index) in resumeData.sections.education"
                :key="`edu-${index}`"
                class="education-card"
              >
                <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start">
                  <div class="flex-1">
                    <h3 class="text-lg font-bold text-gray-900">{{ edu.degree }}</h3>
                    <p class="text-primary-600 font-semibold">{{ edu.institution }}</p>
                    <p v-if="edu.location" class="text-gray-500">{{ edu.location }}</p>
                    <p v-if="edu.gpa" class="text-sm text-gray-600 mt-1">
                      GPA: {{ edu.gpa }}
                    </p>
                    <p v-if="edu.honors" class="text-sm text-gray-600">
                      {{ edu.honors }}
                    </p>
                  </div>
                  <div class="text-sm text-gray-500 mt-2 lg:mt-0 lg:text-right">
                    <p class="font-medium">{{ formatEducationDate(edu) }}</p>
                  </div>
                </div>

                <!-- Relevant Coursework -->
                <div v-if="edu.relevant_coursework?.length" class="mt-3">
                  <p class="text-sm font-medium text-gray-700 mb-1">
                    Relevant Coursework:
                  </p>
                  <p class="text-sm text-gray-600">
                    {{ edu.relevant_coursework.join(", ") }}
                  </p>
                </div>

                <!-- Description -->
                <div v-if="edu.description" class="mt-3">
                  <p class="text-gray-700">{{ edu.description }}</p>
                </div>
              </div>
            </div>
          </section>

          <!-- Projects -->
          <section v-if="resumeData.sections?.projects?.length" class="mb-8">
            <h2 class="section-header">Projects</h2>
            <div class="space-y-6">
              <div
                v-for="(project, index) in resumeData.sections.projects"
                :key="`project-${index}`"
                class="project-card"
              >
                <div
                  class="flex flex-col lg:flex-row lg:justify-between lg:items-start mb-3"
                >
                  <h3 class="text-lg font-bold text-gray-900">
                    {{ project.name || project.title }}
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
                <div v-if="project.technologies?.length" class="mb-3">
                  <p class="text-sm font-medium text-gray-700 mb-2">Technologies:</p>
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="tech in project.technologies"
                      :key="tech"
                      class="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                    >
                      {{ tech }}
                    </span>
                  </div>
                </div>

                <!-- Outcomes -->
                <div v-if="project.outcomes" class="text-sm text-gray-600">
                  <strong>Outcomes:</strong> {{ project.outcomes }}
                </div>
              </div>
            </div>
          </section>

          <!-- Certifications -->
          <section v-if="resumeData.sections?.certifications?.length" class="mb-8">
            <h2 class="section-header">Certifications</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="(cert, index) in resumeData.sections.certifications"
                :key="`cert-${index}`"
                class="flex items-center p-3 border border-gray-200 rounded-lg"
              >
                <svg
                  class="w-5 h-5 text-green-600 mr-3 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clip-rule="evenodd"
                  ></path>
                </svg>
                <span class="text-gray-900 font-medium">{{ cert }}</span>
              </div>
            </div>
          </section>

          <!-- Additional Sections -->
          <section v-if="resumeData.sections?.additional_sections" class="mb-8">
            <!-- Languages -->
            <div
              v-if="resumeData.sections.additional_sections.languages?.length"
              class="mb-6"
            >
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Languages</h3>
              <div class="flex flex-wrap gap-3">
                <span
                  v-for="(language, index) in resumeData.sections.additional_sections
                    .languages"
                  :key="`lang-${index}`"
                  class="inline-block px-3 py-1.5 bg-green-100 text-green-800 rounded-full text-sm"
                >
                  {{ language }}
                </span>
              </div>
            </div>

            <!-- Awards -->
            <div
              v-if="resumeData.sections.additional_sections.awards?.length"
              class="mb-6"
            >
              <h3 class="text-lg font-semibold text-gray-900 mb-3">
                Awards & Recognition
              </h3>
              <ul class="space-y-2">
                <li
                  v-for="(award, index) in resumeData.sections.additional_sections.awards"
                  :key="`award-${index}`"
                  class="flex items-start"
                >
                  <svg
                    class="w-5 h-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                    ></path>
                  </svg>
                  <span class="text-gray-700">{{ award }}</span>
                </li>
              </ul>
            </div>

            <!-- Publications -->
            <div
              v-if="resumeData.sections.additional_sections.publications?.length"
              class="mb-6"
            >
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Publications</h3>
              <ul class="space-y-2">
                <li
                  v-for="(publication, index) in resumeData.sections.additional_sections
                    .publications"
                  :key="`pub-${index}`"
                  class="text-gray-700"
                >
                  {{ publication }}
                </li>
              </ul>
            </div>

            <!-- Volunteer Experience -->
            <div
              v-if="resumeData.sections.additional_sections.volunteer_experience?.length"
              class="mb-6"
            >
              <h3 class="text-lg font-semibold text-gray-900 mb-3">
                Volunteer Experience
              </h3>
              <ul class="space-y-2">
                <li
                  v-for="(volunteer, index) in resumeData.sections.additional_sections
                    .volunteer_experience"
                  :key="`volunteer-${index}`"
                  class="text-gray-700"
                >
                  {{ volunteer }}
                </li>
              </ul>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useFirebase } from "@/composables/useFirebase";
import { useToast } from "@/composables/useToast";

const props = defineProps({
  resumeId: {
    type: String,
    required: false,
  },
});

const resumeData = ref({
  sections: {},
  profile: {},
});

const resumeMetadata = ref(null);
const loading = ref(true);
const error = ref(null);
const exporting = ref(false);
const regenerating = ref(false);
const showExportMenu = ref(false);
const exportDropdown = ref(null);

const { waitForAuth } = useFirebase();
const { success, error: showError } = useToast();

const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

// Helper methods
const formatIndustry = (industry) => {
  return industry.charAt(0).toUpperCase() + industry.slice(1).replace("_", " ");
};

const formatTemplate = (template) => {
  return template.charAt(0).toUpperCase() + template.slice(1);
};

const formatSkillCategory = (category) => {
  return category.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase());
};

const getContactInfo = () => {
  const personal = resumeData.value.sections?.personal_info || {};
  const contact = resumeData.value.sections?.contact_info || {};
  const profile = resumeData.value.profile || {};

  return {
    email: personal.email || contact.email || profile.email || "",
    phone: personal.phone || contact.phone || profile.phone || "",
    location: personal.location || contact.location || profile.location || "",
    linkedin: personal.linkedin || contact.linkedin || profile.linkedin || "",
  };
};

const formatDateRange = (startDate, endDate, isCurrent = false) => {
  if (!startDate) return "N/A";
  const start = formatDate(startDate);
  const end = isCurrent || !endDate ? "Present" : formatDate(endDate);
  return `${start} - ${end}`;
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  try {
    // Handle various date formats
    if (typeof dateString === "number") {
      return dateString.toString();
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

const formatEducationDate = (edu) => {
  if (edu.graduation_date) {
    return formatDate(edu.graduation_date);
  }

  if (edu.endYear) {
    return edu.startYear ? `${edu.startYear} - ${edu.endYear}` : edu.endYear.toString();
  }

  return edu.startYear ? edu.startYear.toString() : "N/A";
};

const getResumeId = () => {
  return props.resumeId || new URLSearchParams(window.location.search).get("id");
};

const loadResume = async () => {
  const resumeId = getResumeId();

  if (!resumeId) {
    error.value = "No resume ID provided";
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    const user = await waitForAuth();
    if (!user) {
      showError("Please log in to view your resume");
      setTimeout(() => (window.location.href = "/login"), 1500);
      return;
    }

    const token = await user.getIdToken();
    const response = await fetch(`${API_URL}/api/v1/resume/${resumeId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error("Resume not found");
      } else if (response.status === 403) {
        throw new Error("You do not have permission to view this resume");
      } else {
        throw new Error(`Failed to load resume (${response.status})`);
      }
    }

    const data = await response.json();

    console.log("Resume Data =====>>>>>>", data);

    // Store both resume content and metadata
    resumeData.value = {
      sections: data.sections || data.ai_content || {},
      profile: data.profile_data || {},
    };

    resumeMetadata.value = {
      id: data.id,
      title: data.title,
      target_job_title: data.target_job_title,
      target_job_role: data.target_job_role,
      industry: data.industry,
      template_id: data.template_id,
      word_count: data.word_count,
      sections_count: data.sections_count,
      created_at: data.created_at,
      export_status: data.export_status,
    };
  } catch (err) {
    console.error("Error loading resume:", err);
    error.value = err.message || "Failed to load resume";
    showError(err.message || "Failed to load resume");
  } finally {
    loading.value = false;
  }
};

const exportResume = async (format) => {
  try {
    exporting.value = true;
    showExportMenu.value = false;

    const resumeId = getResumeId();
    const user = await waitForAuth();

    if (!user) {
      showError("Please log in to export your resume");
      return;
    }

    const token = await user.getIdToken();

    // Start export
    const exportResponse = await fetch(
      `${API_URL}/api/v1/resume/export/${resumeId}/export`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resumeId: resumeId,
          format: format,
          content: resumeData.value.sections,
        }),
      }
    );

    if (!exportResponse.ok) {
      const errorData = await exportResponse.json();
      if (errorData.message === "export_limit_reached") {
        showError(
          "You've reached your monthly export limit. Please upgrade to continue."
        );
        return;
      }
      throw new Error(errorData.message || "Failed to start export");
    }

    const exportData = await exportResponse.json();

    if (exportData.message === "export_limit_reached") {
      showError("You've reached your monthly export limit. Please upgrade to continue.");
      return;
    }

    // Poll for completion
    const pollInterval = setInterval(async () => {
      try {
        const statusResponse = await fetch(
          `${API_URL}/api/v1/resume/export/${exportData.download_url
            .split("/")
            .pop()}/status`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (statusResponse.ok) {
          const statusData = await statusResponse.json();

          if (statusData.status === "completed") {
            clearInterval(pollInterval);

            // Download the file
            const downloadResponse = await fetch(exportData.download_url, {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            });

            if (downloadResponse.ok) {
              const blob = await downloadResponse.blob();
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement("a");
              link.href = url;
              link.download = exportData.filename;
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              window.URL.revokeObjectURL(url);

              success(`Resume exported as ${format.toUpperCase()} successfully!`);
            }
          } else if (statusData.status === "failed") {
            clearInterval(pollInterval);
            throw new Error(statusData.error_message || "Export failed");
          }
        }
      } catch (err) {
        clearInterval(pollInterval);
        console.error("Error checking export status:", err);
        showError("Error during export process");
      }
    }, 2000);

    // Timeout after 2 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      if (exporting.value) {
        showError("Export is taking longer than expected. Please try again.");
        exporting.value = false;
      }
    }, 120000);
  } catch (err) {
    console.error("Error exporting resume:", err);
    showError(err.message || "Failed to export resume");
  } finally {
    exporting.value = false;
  }
};

const regenerateContent = async () => {
  try {
    regenerating.value = true;
    const resumeId = getResumeId();
    const user = await waitForAuth();

    if (!user) {
      showError("Please log in to regenerate content");
      return;
    }

    const token = await user.getIdToken();
    const response = await fetch(`${API_URL}/api/v1/resume/regenerate/${resumeId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to regenerate content");
    }

    const data = await response.json();

    // Update the resume data with new content
    resumeData.value.sections = data.sections;
    success("Resume content regenerated successfully!");
  } catch (err) {
    console.error("Error regenerating content:", err);
    showError(err.message || "Failed to regenerate content");
  } finally {
    regenerating.value = false;
  }
};

const editResume = () => {
  const resumeId = getResumeId();
  window.location.href = `/builder?edit=${resumeId}`;
};

const goBack = () => {
  window.location.href = "/dashboard";
};

const toggleExportMenu = () => {
  showExportMenu.value = !showExportMenu.value;
};

// Click outside to close export menu
const handleClickOutside = (event) => {
  if (exportDropdown.value && !exportDropdown.value.contains(event.target)) {
    showExportMenu.value = false;
  }
};

// Initialize
onMounted(() => {
  loadResume();
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
.section-header {
  @apply text-2xl font-bold text-gray-900 mb-4 pb-2 border-b-2 border-primary-500;
}

.experience-card {
  @apply border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow bg-gray-50;
}

.education-card {
  @apply border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow bg-gray-50;
}

.project-card {
  @apply border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow bg-gray-50;
}

.skill-category {
  @apply border border-gray-200 rounded-lg p-4 bg-gray-50;
}

.prose {
  @apply max-w-none;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Print styles */
@media print {
  .bg-gradient-to-r {
    background: white !important;
  }

  .shadow-lg {
    box-shadow: none !important;
  }

  .border {
    border: 1px solid #e5e7eb !important;
  }
}
</style>
