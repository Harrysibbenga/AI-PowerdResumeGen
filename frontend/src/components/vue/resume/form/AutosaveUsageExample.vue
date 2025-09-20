<!-- Usage Example Component -->
<template name="AutosaveUsageExample">
  <div class="p-6">
    <h2 class="text-xl font-semibold mb-4">Autosave Usage Example</h2>

    <!-- This shows how to use the enhanced form -->
    <div class="space-y-4">
      <div class="bg-gray-50 p-4 rounded-lg">
        <h3 class="font-medium mb-2">Key Features:</h3>
        <ul class="text-sm text-gray-600 space-y-1">
          <li>✅ Automatic saving every 3 seconds (configurable)</li>
          <li>✅ Visual status indicator showing save state</li>
          <li>✅ Manual save button for immediate saves</li>
          <li>✅ Settings panel to customize autosave behavior</li>
          <li>✅ Retry mechanism for failed saves</li>
          <li>✅ Unsaved changes warning before navigation</li>
          <li>✅ Storage size monitoring</li>
          <li>✅ Browser compatibility checks</li>
        </ul>
      </div>

      <div class="bg-blue-50 p-4 rounded-lg">
        <h3 class="font-medium mb-2 text-blue-900">Implementation Benefits:</h3>
        <ul class="text-sm text-blue-800 space-y-1">
          <li>
            🚀 <strong>Better UX:</strong> No more lost work due to accidental page
            refresh
          </li>
          <li>🔄 <strong>Seamless:</strong> Works automatically in the background</li>
          <li>
            ⚙️ <strong>Configurable:</strong> Users can adjust settings to their
            preference
          </li>
          <li>🛡️ <strong>Reliable:</strong> Includes retry logic and error handling</li>
          <li>📱 <strong>Responsive:</strong> Clear visual feedback on save status</li>
        </ul>
      </div>

      <div class="bg-green-50 p-4 rounded-lg">
        <h3 class="font-medium mb-2 text-green-900">How to Use:</h3>
        <ol class="text-sm text-green-800 space-y-1 list-decimal list-inside">
          <li>Import the <code>useResumeData</code> composable in your form component</li>
          <li>Add the <code>AutosaveIndicator</code> component to show save status</li>
          <li>The composable automatically handles data normalization and saving</li>
          <li>Users see real-time feedback on their save status</li>
          <li>Form data is preserved even if they accidentally leave the page</li>
        </ol>
      </div>
    </div>
  </div>
</template>
