// src/api/bookService.js
import axios from 'axios'

// Создаем инстанс axios для запросов к книгам
const apiClient = axios.create({
  baseURL: '/api/books', // Базовый путь для всех запросов
  headers: { 'Content-Type': 'application/json' }
})

// Добавляем JWT токен ко всем запросам
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Получить список книг с фильтрацией и пагинацией
 * В реальности: GET /api/books?search=...&genre=...&year=...&page=1&limit=10
 */
export async function fetchBooks({ search = '', genre = '', year = '', page = 1, limit = 10 } = {}) {
  const params = { page, limit }
  if (search) params.search = search
  if (genre) params.genre = genre
  if (year) params.year = year

  try {
    const response = await apiClient.get('/', { params })
    return response.data // Возвращаем { data: [...], total: ... }
  } catch (error) {
    console.error('Ошибка при загрузке книг:', error)
    throw error
  }
}

/**
 * Получить детальную информацию о книге
 * В реальности: GET /api/books/:id
 */
export async function fetchBookById(id) {
  try {
    const response = await apiClient.get(`/${id}`)
    return response.data
  } catch (error) {
    console.error(`Ошибка при загрузке книги ${id}:`, error)
    throw error
  }
}

/**
 * Получить статус книги на основе экземпляров (Логика фронтенда)
 * Эту функцию оставляем, так как она вычисляет метку для UI на основе данных с сервера
 */
export function computeBookStatus(book) {
  // Если данные приходят в формате { copies: [...] }
  const copies = book.copies || book
  
  if (!copies?.length) return { label: 'Неизвестно', class: 'secondary' }
  
  const available = copies.filter(c => c.status === 'available').length
  if (available === 0) return { label: 'Нет в наличии', class: 'danger' }
  if (available < copies.length) return { label: 'Мало', class: 'warning' }
  
  return { label: 'В наличии', class: 'success' }
}

/**
 * Забронировать книгу
 * ВНИМАНИЕ: Эндпоинт для брони пока не реализован на бэкенде (только GET запросы).
 * Оставляем как заглушку или подготовленный запрос.
 */
export async function reserveBook({ bookId, copyId, userId }) {
  // TODO: Когда напишем POST /api/books/:id/reserve на бэкенде, раскомментировать:
  /*
  const response = await apiClient.post(`/${bookId}/reserve`, { copyId, userId })
  return response.data
  */

  // Пока возвращаем мок-успех, чтобы интерфейс не падал
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        success: true,
        reservationId: Date.now(),
        message: 'Бронь оформлена (Mock, бэкенд в разработке)'
      })
    }, 500)
  })
}