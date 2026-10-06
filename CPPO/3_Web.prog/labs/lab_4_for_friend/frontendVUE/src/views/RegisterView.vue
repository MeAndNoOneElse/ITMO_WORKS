<template>
  <div class="page-container">
    <header class="header">
      <div class="header-info">
        <span><b>ФИО:</b>Федяев Михаил Дмитриевич</span>
        <span><b>Группа:</b> P3219</span>
        <span><b>Вариант:</b> 454</span>
      </div>
    </header>

    <main class="main-content">
      <div class="auth-box">
        <h1>Регистрация</h1>

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
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="Введите email (необязательно)"
            :class="{ 'input-error': errors.email }"
            @input="clearError('email')"
          />
          <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Минимум 6 символов"
            :class="{ 'input-error': errors.password }"
            @input="clearError('password')"
          />
          <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label for="confirm">Подтверждение пароля</label>
          <input
            id="confirm"
            v-model="form.confirm"
            type="password"
            placeholder="Повторите пароль"
            :class="{ 'input-error': errors.confirm }"
            @input="clearError('confirm')"
            @keydown.enter="onRegister"
          />
          <span v-if="errors.confirm" class="error-text">{{ errors.confirm }}</span>
        </div>

        <div v-if="serverError" class="alert alert-error">{{ serverError }}</div>

        <div class="actions">
          <button class="btn-primary" :disabled="loading" @click="onRegister">
            <span v-if="loading">Регистрация...</span>
            <span v-else>Зарегистрироваться</span>
          </button>
        </div>

        <div class="register-link">
          <p>Уже есть аккаунт? <RouterLink to="/login" class="link">Войти</RouterLink></p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter, RouterLink } from 'vue-router';
import { register } from '../services/authService';

const router = useRouter();

const form = reactive({ username: '', email: '', password: '', confirm: '' });
const errors = reactive({ username: '', email: '', password: '', confirm: '' });
const serverError = ref('');
const loading = ref(false);

function clearError(field: keyof typeof errors) {
  errors[field] = '';
  serverError.value = '';
}

function validate(): boolean {
  let valid = true;

  if (!form.username || form.username.trim().length < 3) {
    errors.username = 'Логин должен содержать минимум 3 символа';
    valid = false;
  }

  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Введите корректный email';
    valid = false;
  }

  if (!form.password || form.password.length < 6) {
    errors.password = 'Пароль должен содержать минимум 6 символов';
    valid = false;
  }

  if (form.password !== form.confirm) {
    errors.confirm = 'Пароли не совпадают';
    valid = false;
  }

  return valid;
}

async function onRegister() {
  if (!validate()) return;

  loading.value = true;
  serverError.value = '';

  try {
    const res = await register({
      username: form.username.trim(),
      email: form.email || undefined,
      password: form.password
    });
    if (res.success) {
      router.push('/main');
    } else {
      serverError.value = res.message || 'Ошибка регистрации';
    }
  } catch (err: any) {
    serverError.value = err.response?.data?.message || 'Имя пользователя уже занято';
  } finally {
    loading.value = false;
  }
}
</script>

