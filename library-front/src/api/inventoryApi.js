// src/api/inventoryApi.js
import api from './client'

// === API ФУНКЦИИ (Реальные запросы к FastAPI) ===

export async function fetchBooksApi() {
  const response = await api.get('/inventory/books')
  return response.data
}

export async function addBookApi(bookData) {
  const response = await api.post('/inventory/books', bookData)
  // Возвращаем структуру, ожидаемую сторами
  return { id: response.data.id, ...bookData, copies: [{ id: Date.now(), status: 'available', location: 'Новое поступление' }] }
}

export async function updateBookApi(id, bookData) {
  // Пока нет отдельного эндпоинта обновления, можно реализовать PUT /inventory/books/:id
  // Заглушка с реальным вызовом, когда добавишь на бэкенд
  console.warn('PUT /inventory/books/:id not implemented yet')
  return { id, ...bookData }
}

export async function deleteBookApi(id) {
  console.warn('DELETE /inventory/books/:id not implemented yet')
  return true
}

export async function fetchFinesApi() {
  const response = await api.get('/inventory/fines')
  return response.data
}

export async function markFineAsPaidApi(fineId) {
  const response = await api.patch(`/inventory/fines/${fineId}/pay`)
  return response.data
}

export async function fetchReservationsApi() {
  const response = await api.get('/inventory/reservations')
  return response.data
}

export async function approveReservationApi(resId) {
  const response = await api.patch(`/inventory/reservations/${resId}/approve`)
  return response.data
}

export async function cancelReservationApi(resId) {
  const response = await api.delete(`/inventory/reservations/${resId}`)
  return response.data
}

export async function fulfillReservationApi(resId) {
  const response = await api.patch(`/inventory/reservations/${resId}/fulfill`)
  return response.data
}

export async function checkoutBookApi({ copyId, userId, userName, reservationId }) {
  const payload = { copyId, userId, userName }
  if (reservationId) payload.reservationId = reservationId
  const response = await api.post('/inventory/checkout', payload)
  return { success: true, dueDate: response.data.dueDate || new Date(Date.now() + 14*24*60*60*1000).toISOString(), message: response.data.message }
}

export async function returnBookApi(copyId) {
  const response = await api.post('/inventory/return', { copyId })
  return { success: true, message: response.data.message }
}

export async function fetchRecentActivitiesApi({ limit = 5 } = {}) {
  const response = await api.get('/inventory/activities', { params: { limit } })
  return response.data
}

// === Утилиты для статистики (Оставляем на фронтенде) ===

export function computeInventoryStats(books) {
  const totalBooks = books.length
  const totalCopies = books.reduce((acc, b) => acc + (b.copies?.length || 0), 0)
  const availableCopies = books.reduce((acc, b) =>
    acc + (b.copies?.filter(c => c.status === 'available').length || 0), 0)
  return { totalBooks, totalCopies, availableCopies }
}

export function computeFinesStats(fines) {
  const unpaid = fines.filter(f => !f.paid)
  const totalUnpaidAmount = unpaid.reduce((acc, f) => acc + (f.amount || 0), 0)
  return { unpaidFines: unpaid, totalUnpaidAmount }
}