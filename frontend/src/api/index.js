// frontend\src\api\index.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Можно добавить интерсепторы
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Логирование ошибок в консоль (или в Sentry)
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;