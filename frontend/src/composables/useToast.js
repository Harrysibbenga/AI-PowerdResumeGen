// src/composables/useToast.js
import { ref, reactive } from 'vue';

const toasts = ref([]);
let toastId = 0;

export const useToast = () => {
  const addToast = (message, type = 'info', duration = 3000) => {
    const id = toastId++;
    const toast = {
      id,
      message,
      type,
      visible: true
    };
    
    toasts.value.push(toast);
    
    setTimeout(() => {
      removeToast(id);
    }, duration);
    
    return id;
  };
  
  const removeToast = (id) => {
    const index = toasts.value.findIndex(toast => toast.id === id);
    if (index > -1) {
      toasts.value.splice(index, 1);
    }
  };
  
  const success = (message, duration) => addToast(message, 'success', duration);
  const error = (message, duration) => addToast(message, 'error', duration);
  const info = (message, duration) => addToast(message, 'info', duration);
  const warning = (message, duration) => addToast(message, 'warning', duration);
  
  return {
    toasts,
    success,
    error,
    info,
    warning,
    removeToast
  };
};