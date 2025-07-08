<template>
  <div class="col-span-full">
    <div class="border border-gray-200 rounded-lg p-12 text-center bg-gray-50">
      <div
        class="mx-auto w-16 h-16 mb-4 flex items-center justify-center bg-primary-100 rounded-full"
      >
        <svg
          class="w-8 h-8 text-primary-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          ></path>
        </svg>
      </div>

      <h3 class="text-lg font-semibold text-gray-900 mb-2">No Resumes Yet</h3>
      <p class="text-gray-600 mb-6 max-w-md mx-auto">
        Get started by creating your first resume. Our AI-powered builder will help you
        create a professional resume in minutes.
      </p>

      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <a
          href="/builder"
          class="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
        >
          Create Your First Resume
        </a>

        <a
          href="/templates"
          class="border border-gray-300 hover:border-gray-400 text-gray-700 px-6 py-3 rounded-lg transition-colors font-medium"
        >
          Browse Templates
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "NoResumesFound",
};
</script>
