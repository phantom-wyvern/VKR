// src/api/bookApi.js
import api from './client' // Импортируем настроенный axios

/**
 * Получить список книг с фильтрацией и пагинацией
 * GET /api/books/?search=...&genre=...&year=...&status=...&page=1&limit=20
 */
export async function fetchBooksApi({ search = '', genre = '', year = '', status = '', page = 1, limit = 20 } = {}) {
  const params = { page, limit }
  if (search) params.search = search
  if (genre) params.genre = genre
  if (year) params.year = year
  if (status) params.status = status

  // Trailing slash важен для FastAPI (избегает редиректа)
  const response = await api.get('/books/', { params })

  return response.data
}

/**
 * Получить детальную информацию о книге
 * GET /api/books/:id
 */
export async function fetchBookByIdApi(id) {
  const response = await api.get(`/books/${id}`)
  return response.data
}

/**
 * Получить список жанров для фильтра
 * GET /api/books/filters/genres
 */
export async function fetchGenresApi() {
  const response = await api.get('/books/filters/genres')
  return response.data
}

/**
 * Получить список годов для фильтра
 * GET /api/books/filters/years
 */
export async function fetchYearsApi() {
  const response = await api.get('/books/filters/years')
  return response.data
}

/**
 * Забронировать книгу
 * POST /api/loans/reserve?book_id={bookId}
 */
export async function reserveBookApi({ bookId }) {
  try {
    const response = await api.post('/loans/reserve', null, {
      params: { book_id: bookId }
    })
    return response.data
  } catch (error) {
    // Пробрасываем ошибку дальше для обработки в вызывающем коде
    throw error
  }
}

/**
 * Вычисление статуса книги (логика фронтенда)
 */
export function computeBookStatus(copies) {
  if (!copies?.length) return { label: 'Неизвестно', class: 'secondary' }
  const available = copies.filter(c => c.status === 'available').length
  const total = copies.length
  
  if (available === total) return { label: 'В наличии', class: 'success' }
  if (available === 0) return { label: 'Нет в наличии', class: 'danger' }
  return { label: `Мало (${available}/${total})`, class: 'warning' }
}