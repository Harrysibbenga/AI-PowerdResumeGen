<script setup>
import { onMounted, getCurrentInstance } from "vue";
import Toast from "vue-toast-notification";

onMounted(() => {
  const app = getCurrentInstance()?.appContext.app;

  // Prevent multiple installs (especially on HMR reload)
  if (app && !app._toastInstalled) {
    app.use(Toast, {
      position: "top-right",
      duration: 3000,
      dismissible: true,
      queue: true,
    });
    app._toastInstalled = true;
  }
});
</script>

<template>
  <!-- Hidden component used for mounting toast plugin globally -->
  <div></div>
</template>
