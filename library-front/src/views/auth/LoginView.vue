<template>
  <div class="auth-page">
    <div class="auth-card glass animate-fade-in">
      
      <!-- Header -->
      <div class="auth-header">
        <div class="auth-icon">
          <i class="pi pi-sign-in"></i>
        </div>
        <h1 class="auth-title">Вход в систему</h1>
        <p class="auth-subtitle">Введите учетные данные для доступа</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label class="form-label">Email</label>
          <InputText v-model="form.email" placeholder="reader@mail.ru" class="w-full" autofocus />
        </div>

        <div class="form-group">
          <label class="form-label">Пароль</label>
          <Password 
            v-model="form.password" 
            placeholder="••••••••" 
            toggleMask 
            :feedback="false" 
            class="w-full" 
          />
        </div>

        <Message v-if="error" severity="error" class="auth-error">
          {{ error }}
        </Message>

        <Button label="Войти" :loading="loading" type="submit" class="w-full" />
      </form>

      <!-- Footer -->
      <div class="auth-footer">
        <span class="text-secondary">Нет аккаунта?</span>
        <router-link to="/register" class="auth-link">Зарегистрироваться</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const auth = useAuthStore()
const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  
  // Простая валидация перед запросом
  if (!form.value.email.trim() || !form.value.password.trim()) {
    error.value = 'Заполните все поля'
    return
  }

  loading.value = true
  try {
    // auth.login теперь возвращает { success, error } и сам делает редирект при успехе
    const result = await auth.login(form.value)
    if (!result.success) {
      error.value = result.error || 'Неверный email или пароль'
    }
  } catch (e) {
    error.value = e.message || 'Ошибка соединения'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background-color: var(--surface-0);
}

.auth-card {
  padding: 36px 28px;
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 440px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
}

.auth-header {
  text-align: center;
  margin-bottom: 28px;
}
.auth-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: rgba(187, 134, 252, 0.15);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  color: var(--primary);
  font-size: 22px;
}
.auth-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 6px 0;
}
.auth-subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
  display: block;
}
.auth-error {
  margin-bottom: 0;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: var(--text-secondary);
  display: flex;
  justify-content: center;
  gap: 8px;
}
.auth-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s;
}
.auth-link:hover { opacity: 0.8; }
</style>