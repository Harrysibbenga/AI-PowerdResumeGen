// src/plugins/toast.js
import Toast, { POSITION } from "vue-toast-notification";
import "vue-toast-notification/dist/index.css";

export default {
  install(app) {
    app.use(Toast, {
      position: POSITION.TOP_RIGHT,
      timeout: 3000,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
    });
  }
};
