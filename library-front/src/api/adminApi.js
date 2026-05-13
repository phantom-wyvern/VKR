// src/api/adminApi.js
import axios from 'axios'

const API_BASE = '/api/admin'

// Настройка axios инстанса (можно переиспользовать из authApi или создать новый)
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
})

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// --- Users ---
export async function fetchUsersApi() {
  const response = await apiClient.get('/users')
  return response.data
}

export async function createUserApi(userData) {
  const response = await apiClient.post('/users', userData)
  return response.data
}

export async function updateUserApi(id, userData) {
  const response = await apiClient.put(`/users/${id}`, userData)
  return response.data
}

export async function deleteUserApi(id) {
  const response = await apiClient.delete(`/users/${id}`)
  return response.data
}

export async function toggleUserStatusApi(id) {
  const response = await apiClient.patch(`/users/${id}/toggle-status`)
  return response.data
}

// --- Settings ---
export async function fetchSettingsApi() {
  const response = await apiClient.get('/settings')
  return response.data
}

export async function saveSettingsApi(newSettings) {
  const response = await apiClient.put('/settings', newSettings)
  return response.data
}

// --- Genres ---
export async function fetchGenresApi() {
  const response = await apiClient.get('/genres')
  return response.data
}

export async function addGenreApi(name) {
  const response = await apiClient.post('/genres', { name })
  return response.data
}

export async function updateGenreApi(id, { name }) {
  const response = await apiClient.put(`/genres/${id}`, { name })
  return response.data
}

export async function deleteGenreApi(id) {
  const response = await apiClient.delete(`/genres/${id}`)
  return response.data
}

// --- Audit Logs ---
export async function fetchAuditLogsApi({ search = '', startDate = null, endDate = null, page = 1, limit = 20 } = {}) {
  const params = { page, limit }
  if (search) params.search = search
  if (startDate) params.startDate = startDate
  if (endDate) params.endDate = endDate
  const response = await apiClient.get('/audit', { params })
  return response.data
}