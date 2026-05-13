// src/api/client.js
import axios from 'axios'

// Базовый URL: используем относительный путь для Vite proxy
// ВАЖНО: VITE_API_URL должен быть '/api', а не полным URL домена
let baseURL = import.meta.env.VITE_API_URL

// Если VITE_API_URL не задан или пустой — используем относительный путь
if (!baseURL) {
  baseURL = '/api'
}

// Дополнительная проверка: если baseURL содержит полный URL домена,
// это означает что переменная окружения настроена неправильно.
// В этом случае принудительно используем '/api'
if (baseURL.startsWith('http://') || baseURL.startsWith('https://')) {
  console.error(
    '[API Client] VITE_API_URL содержит полный URL домена (' + baseURL + '). ' +
    'Это ломит Vite proxy! Принудительно использую "/api". ' +
    'Исправьте VITE_API_URL в .env файле.'
  )
  baseURL = '/api'
}

// Убедимся, что baseURL не заканчивается на '/' (axios сам добавит)
baseURL = baseURL.replace(/\/+$/, '')

const api = axios.create({
  baseURL: baseURL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Debug: логируем baseURL при загрузке (только в dev режиме)
if (import.meta.env.DEV) {
  console.log('[API Client] baseURL:', baseURL)
}

// Request interceptor: add auth token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  config.metadata = { startTime: new Date() }
  return config
})

// Response interceptor: handle errors globally
api.interceptors.response.use(
  res => {
    if (import.meta.env.DEV && res.config.metadata) {
      const duration = new Date() - res.config.metadata.startTime
      console.debug(`[API] ${res.config.url} - ${duration}ms`)
    }
    return res
  },
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('auth_token')
    }
    if (import.meta.env.DEV) {
      console.error('[API Error]', {
        url: err.config?.url,
        status: err.response?.status,
        message: err.message
      })
    }
    return Promise.reject(err)
  }
)

export default api