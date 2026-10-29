// frontend\src\composables\useLeads.js
import { ref } from 'vue';
import api from '@/api';

export function useLeads() {
  const loading = ref(false);
  const message = ref('');
  const isError = ref(false);

  const submitLead = async (payload) => {
    loading.value = true;
    message.value = '';
    isError.value = false;

    try {
      const { data } = await api.post('/leads/', payload);
      message.value = data.message || 'Спасибо! Я свяжусь с вами в ближайшее время.';
      return true;
    } catch (error) {
      message.value = error.response?.data?.error || 'Ошибка отправки. Попробуйте позже.';
      isError.value = true;
      return false;
    } finally {
      loading.value = false;
    }
  };

  return { loading, message, isError, submitLead };
}