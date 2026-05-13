// src/api/reportsApi.js
import api from './client' // Используем настроенный axios-инстанс

/**
 * Получить данные для графика выдач по месяцам
 * В реальности: GET /api/reports/loans-by-month?months=6
 */
export async function fetchLoansByMonthApi({ months = 6 } = {}) {
  const response = await api.get('/reports/loans-by-month', { params: { months } })
  return response.data
}

/**
 * Получить данные для графика активности по дням недели
 * В реальности: GET /api/reports/activity-by-day
 */
export async function fetchActivityByDayApi() {
  const response = await api.get('/reports/activity-by-day')
  return response.data
}

/**
 * Получить распределение по жанрам
 * В реальности: GET /api/reports/genres-distribution?limit=10
 */
export async function fetchGenresDistributionApi({ limit = 10 } = {}) {
  const response = await api.get('/reports/genres-distribution', { params: { limit } })
  return response.data
}

/**
 * Получить топ популярных книг
 * В реальности: GET /api/reports/top-books?limit=5&period=all
 */
export async function fetchTopBooksApi({ limit = 5, period = 'all' } = {}) {
  const response = await api.get('/reports/top-books', { params: { limit, period } })
  return response.data
}

/**
 * Получить общую статистику
 * В реальности: GET /api/reports/stats
 */
export async function fetchReportsStatsApi() {
  const response = await api.get('/reports/stats')
  return response.data
}