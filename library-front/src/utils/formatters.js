// src/utils/formatters.js

/**
 * Форматирует роль в человекочитаемое название
 */
export const getRoleName = (role) => {
  const names = {
    reader: 'Читатель',
    librarian: 'Библиотекарь',
    admin: 'Администратор'
  }
  return names[role] || role
}

/**
 * Форматирует дату в локальный формат
 */
export const formatDate = (dateString, options = {}) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options
  })
}

/**
 * Форматирует сумму в рублях
 */
export const formatRubles = (amount) => {
  if (amount == null) return '—'
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(amount)
}

/**
 * Форматирует статус книги
 */
export const formatBookStatus = (status) => {
  const labels = {
    available: 'В наличии',
    borrowed: 'Выдана',
    reserved: 'Забронирована',
    lost: 'Утеряна'
  }
  return labels[status] || status
}

/**
 * Получает цветовой индикатор для статуса
 */
export const getStatusSeverity = (status) => {
  const map = {
    available: 'success',
    borrowed: 'info',
    reserved: 'warning',
    lost: 'danger',
    active: 'success',
    blocked: 'danger',
    pending: 'warning'
  }
  return map[status] || 'secondary'
}