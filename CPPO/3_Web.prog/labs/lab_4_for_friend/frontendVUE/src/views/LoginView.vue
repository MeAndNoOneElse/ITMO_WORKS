<template>
  <div class="page-container">
    <header class="header">
      <div class="header-info">
        <span><b>ФИО:</b> Федяев Михаил Дмитриевич</span>
        <span><b>Группа:</b> P3219</span>
        <span><b>Вариант:</b> 454</span>
      </div>
    </header>

    <main class="main-content">
      <div v-if="sessionExpired" class="alert alert-warning">
        <span>Сессия истекла. Пожалуйста, войдите снова.</span>
        <button class="alert-close" @click="sessionExpired = false">✕</button>
      </div>

      <div class="auth-box">
        <h1>Вход</h1>

        <div class="form-group">
          <label for="username">Логин</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            placeholder="Введите логин"
            :class="{ 'input-error': errors.username }"
            @input="clearError('username')"
          />
          <span v-if="errors.username" class="error-text">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Введите пароль"
            :class="{ 'input-error': errors.password }"
            @input="clearError('password')"
            @keydown.enter="onLogin"
          />
          <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
        </div>

        <div v-if="serverError" class="alert alert-error">{{ serverError }}</div>

        <div class="actions">
          <button class="btn-primary" :disabled="loading" @click="onLogin">
            <span v-if="loading">Вход...</span>
            <span v-else>Войти</span>
          </button>
        </div>

        <div class="register-link">
          <p>Нет аккаунта? <RouterLink to="/register" class="link">Зарегистрироваться</RouterLink></p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute, RouterLink } from 'vue-router';
import { login } from '../services/authService';

const router = useRouter();
const route = useRoute();

const form = reactive({ username: '', password: '' });
const errors = reactive({ username: '', password: '' });
const serverError = ref('');
const loading = ref(false);
const sessionExpired = ref(false);

onMounted(() => {
  if (route.query.sessionExpired === 'true') {
    sessionExpired.value = true;
  }
});

function clearError(field: 'username' | 'password') {
  errors[field] = '';
  serverError.value = '';
}

function validate(): boolean {
  let valid = true;
  if (!form.username || form.username.trim().length < 3) {
    errors.username = 'Логин должен содержать минимум 3 символа';
    valid = false;
  }
  if (!form.password || form.password.length < 6) {
    errors.password = 'Пароль должен содержать минимум 6 символов';
    valid = false;
  }
  return valid;
}

async function onLogin() {
  if (!validate()) return;

  loading.value = true;
  serverError.value = '';

  try {
    console.log('[LOGIN] Отправляем запрос логина для пользователя:', form.username);
    const res = await login({ username: form.username.trim(), password: form.password });
    console.log('[LOGIN] Получен ответ:', res);
    if (res.success) {
      console.log('[LOGIN] Успешный логин, перенаправляем на /main');
      router.push('/main');
    } else {
      serverError.value = res.message || 'Ошибка входа';
      console.error('[LOGIN] Ошибка: ' + serverError.value);
    }
  } catch (err: any) {
    console.error('[LOGIN] Исключение:', err);
    console.error('[LOGIN] Ответ сервера:', err.response?.data);
    // Сервер возвращает 401 с JSON { success: false, message: "..." }
    serverError.value =
      err.response?.data?.message ||
      err.response?.data?.error ||
      'Неверный логин или пароль';
  } finally {
    loading.value = false;
  }
}
</script>

