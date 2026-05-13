// src/api/loanApi.js
import api from './client'

/**
 * Получить активные займы текущего пользователя
 * В реальности: GET /api/loans/active
 * (userId игнорируется, бэкенд определяет читателя по JWT)
 */
export async function fetchActiveLoansApi(userId) {
  const response = await api.get('/loans/active')
  return response.data
}

/**
 * Получить историю займов
 * В реальности: GET /api/loans/history?page=1&limit=10
 */
export async function fetchLoanHistoryApi({ page = 1, limit = 10 } = {}) {
  const response = await api.get('/loans/history', { params: { page, limit } })
  return response.data
}

/**
 * Получить бронирования пользователя
 * В реальности: GET /api/loans/reservations
 */
export async function fetchReservationsApi() {
  const response = await api.get('/loans/reservations')
  return response.data
}

/**
 * Продлить займ
 * В реальности: POST /api/loans/:loanId/renew
 */
export async function renewLoanApi(loanId) {
  const response = await api.post(`/loans/${loanId}/renew`)
  return response.data
}

/**
 * Отменить бронирование
 * В реальности: DELETE /api/loans/reservations/:reservationId
 */
export async function cancelReservationApi(resId) {
  const response = await api.delete(`/loans/reservations/${resId}`)
  return response.data
}

/**
 * Вернуть книгу (запрос на возврат)
 * В реальности: POST /api/loans/:loanId/return-request
 */
export async function requestReturnApi(loanId) {
  const response = await api.post(`/loans/${loanId}/return-request`)
  return response.data
}

/**
 * Подтвердить получение забронированной книги
 * В реальности: POST /api/loans/reservations/:reservationId/claim
 */
export async function claimReservationApi(resId) {
  const response = await api.post(`/loans/reservations/${resId}/claim`)
  return response.data
}

/**
 * Оставить оценку книге
 * В реальности: POST /api/loans/:loanId/rate
 */
export async function rateBookApi({ loanId, rating, comment = '' }) {
  const response = await api.post(`/loans/${loanId}/rate`, { rating, comment })
  return response.data
}

// === Утилиты (оставляем на фронтенде для расчёта UI-статистики) ===
export function computeLoanStats(loans) {
  const active = loans.filter(l => l.status === 'active')
  const overdue = loans.filter(l => l.status === 'overdue')
  const totalFine = overdue.reduce((acc, l) => acc + (l.fineAmount || 0), 0)
  return {
    activeCount: active.length,
    overdueCount: overdue.length,
    totalFineAmount: totalFine,
    nextDueDate: active.length > 0
      ? active.sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate))[0].dueDate
      : null
  }
}