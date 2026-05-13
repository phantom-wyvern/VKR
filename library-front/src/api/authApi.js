// src/api/authApi.js
import axios from 'axios'

// Базовый URL API (в Docker-окружении проксируется через Vite)
const API_BASE = '/api'

// Настройка axios инстанса
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Добавление токена к запросам
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Реальный запрос на логин
 * POST /api/auth/login
 */
export async function loginApi({ email, password }) {
  const response = await apiClient.post('/auth/login', { email, password })
  return response.data  // { token, user, expiresAt }
}

/**
 * Реальный запрос на выход
 * POST /api/auth/logout
 */
export async function logoutApi() {
  const response = await apiClient.post('/auth/logout')
  return response.data  // { success, message }
}

/**
 * Реальная регистрация
 * POST /api/auth/register
 */
export async function registerApi({ name, email, password, confirm_password }) {
  const response = await apiClient.post('/auth/register', {
    name,
    email,
    password,
    confirm_password
  })
  return response.data  // { success, message, userId }
}

/**
 * Получить профиль текущего пользователя
 * GET /api/auth/me
 */
export async function fetchMeApi() {
  const response = await apiClient.get('/auth/me')
  return response.data  // { id, name, email, role, permissions }
}