export const FALLBACK_IMAGE = 'https://placehold.co/200x300/e2e8f0/64748b?text=Нет+обложки'
export const FALLBACK_COVER = 'https://placehold.co/200x300/e2e8f0/64748b?text=Нет+обложки'
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
export const BOOK_STATUSES = {
  AVAILABLE: { label: 'В наличии', class: 'success' },
  LOW_STOCK: { label: 'Мало', class: 'warning' },
  UNAVAILABLE: { label: 'Нет в наличии', class: 'danger' },
  UNKNOWN: { label: 'Неизвестно', class: 'secondary' }
}