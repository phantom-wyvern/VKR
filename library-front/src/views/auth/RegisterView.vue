<template>
  <div class="auth-page">
    <div class="auth-card glass animate-fade-in">
      
      <!-- Header -->
      <div class="auth-header">
        <div class="auth-icon warning">
          <i class="pi pi-user-plus"></i>
        </div>
        <h1 class="auth-title">Регистрация</h1>
        <p class="auth-subtitle">Создайте учетную запись для доступа к библиотеке</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label class="form-label">Имя</label>
          <InputText v-model="form.name" placeholder="Иван Иванов" class="w-full" autofocus />
        </div>

        <div class="form-group">
          <label class="form-label">Email</label>
          <InputText v-model="form.email" type="email" placeholder="ivan@example.com" class="w-full" />
        </div>

        <div class="form-group">
          <label class="form-label">Пароль</label>
          <Password v-model="form.password" placeholder="Минимум 6 символов" toggleMask :feedback="false" class="w-full" />
        </div>

        <div class="form-group">
          <label class="form-label">Подтвердите пароль</label>
          <Password v-model="form.confirmPassword" placeholder="Повторите пароль" :feedback="false" class="w-full" />
        </div>

        <Message v-if="error" severity="error" class="auth-error">{{ error }}</Message>
        <Message v-if="successMsg" severity="success" class="auth-error">{{ successMsg }}</Message>

        <Button label="Зарегистрироваться" :loading="loading" type="submit" class="w-full" />
      </form>

      <!-- Footer -->
      <div class="auth-footer">
        <span class="text-secondary">Уже есть аккаунт?</span>
        <router-link to="/login" class="auth-link">Войти</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ name: '', email: '', password: '', confirmPassword: '' })
const loading = ref(false)
const error = ref('')
const successMsg = ref('')

const handleRegister = async () => {
  error.value = ''
  successMsg.value = ''

  // Валидация
  if (!form.value.name.trim() || !form.value.email.trim() || !form.value.password || !form.value.confirmPassword) {
    error.value = 'Заполните все поля'
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    error.value = 'Введите корректный email'
    return
  }
  if (form.value.password !== form.value.confirmPassword) {
    error.value = 'Пароли не совпадают'
    return
  }
  if (form.value.password.length < 6) {
    error.value = 'Пароль должен содержать минимум 6 символов'
    return
  }

  loading.value = true
  try {
    const result = await auth.register(form.value)
    if (result.success) {
      successMsg.value = 'Регистрация успешна! Перенаправление на вход...'
      setTimeout(() => router.push('/login'), 1500)
    } else {
      error.value = result.error || 'Ошибка при регистрации'
    }
  } catch (e) {
    error.value = e.message || 'Ошибка соединения с сервером'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Те же стили, что и в LoginView, для единообразия */
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
.auth-card { padding: 36px 28px; border-radius: var(--radius-lg); width: 100%; max-width: 440px; box-shadow: 0 12px 40px rgba(0,0,0,0.5); }
.auth-header { text-align: center; margin-bottom: 28px; }
.auth-icon { width: 52px; height: 52px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 14px; font-size: 22px; }
.auth-icon.warning { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.auth-title { font-size: 22px; font-weight: 700; color: var(--text-primary); margin: 0 0 6px 0; }
.auth-subtitle { color: var(--text-secondary); font-size: 14px; margin: 0; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.form-label { font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 6px; display: block; }
.auth-error { margin-bottom: 0; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 14px; color: var(--text-secondary); display: flex; justify-content: center; gap: 8px; }
.auth-link { color: var(--primary); text-decoration: none; font-weight: 500; transition: opacity 0.2s; }
.auth-link:hover { opacity: 0.8; }
</style>