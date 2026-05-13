// src/api/librarianService.js
import api from './client' // Используем настроенный axios-инстанс

// Полный список возможных пунктов меню (статика)
const ALL_MENU_ITEMS = [
  { id: 'dashboard', label: 'Главная', icon: 'pi pi-home', path: '/librarian', permission: null },
  { id: 'checkout', label: 'Выдача / Возврат', icon: 'pi pi-sync', path: '/librarian/checkout', permission: 'loans:manage' },
  { id: 'inventory', label: 'Фонд', icon: 'pi pi-list', path: '/librarian/inventory', permission: 'books:read' },
  { id: 'reservations', label: 'Бронирования', icon: 'pi pi-clock', path: '/librarian/reservations', permission: 'reservations:manage' },
  { id: 'loans', label: 'Займы', icon: 'pi pi-book', path: '/librarian/loans', permission: 'loans:manage' },
  { id: 'reports', label: 'Отчёты', icon: 'pi pi-chart-line', path: '/librarian/reports', permission: 'reports:view' }
]

/**
 * Получить данные текущего библиотекаря
 * В реальности: GET /api/auth/me
 */
export async function fetchLibrarianProfile() {
  const response = await api.get('/auth/me')
  return response.data
}

/**
 * Выйти из системы
 * В реальности: POST /api/auth/logout
 */
export async function librarianLogout() {
  await api.post('/auth/logout')
  return { success: true, message: 'Выход выполнен' }
}

/**
 * Получить доступные пункты меню на основе прав текущего пользователя
 * В реальности: GET /api/auth/me -> фильтрация меню
 */
export async function fetchLibrarianMenuItems() {
  // Сначала получаем профиль, чтобы узнать права
  const profile = await fetchLibrarianProfile()
  
  // Фильтруем меню: показываем пункт, если у него нет требования прав (permission: null)
  // ИЛИ если у пользователя есть нужное право
  return ALL_MENU_ITEMS.filter(item => 
    !item.permission || (profile.permissions && profile.permissions.includes(item.permission))
  )
}

/**
 * Получить статистику для дашборда
 * В реальности: GET /api/inventory/stats
 */
export async function fetchLibrarianStats() {
  const response = await api.get('/inventory/stats')
  return response.data
}

/**
 * Проверить право доступа (утилита)
 * Принимает массив прав пользователя и проверяемое право
 */
export function hasPermission(userPermissions, permission) {
  return userPermissions?.includes(permission) || false
}