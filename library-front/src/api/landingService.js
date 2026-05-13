// src/api/landingService.js
import api from './client' // Используем глобальный axios-инстанс с интерцепторами

/**
 * Получить контент главной страницы
 * В реальности: GET /api/landing/content
 */
export async function fetchLandingContent() {
  const response = await api.get('/landing/content')
  return response.data
}