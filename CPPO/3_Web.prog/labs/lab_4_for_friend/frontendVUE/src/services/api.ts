import axios from 'axios';
import { getAccessToken, getRefreshToken, saveTokens, clearTokens } from './authService';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
});

// Request interceptor — добавляем Bearer токен
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — при 401 пробуем refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Не трогаем 401 с эндпоинтов логина/регистрации — там это просто «неверный пароль»
    const url: string = originalRequest?.url || '';
    if (url.includes('/auth/login') || url.includes('/auth/register')) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        const res = await axios.post('/api/auth/refresh', { refreshToken });
        if (res.data.success && res.data.token) {
          saveTokens(res.data.token, res.data.refreshToken || refreshToken);
          originalRequest.headers['Authorization'] = `Bearer ${res.data.token}`;
          return api(originalRequest);
        }
      } catch {
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

