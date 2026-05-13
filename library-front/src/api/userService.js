// src/api/userService.js
import api from './client' // Используем настроенный axios-инстанс

// Статические пункты меню (фильтрация по правам — на фронтенде)
const MENU_ITEMS = [
  { id: 'dashboard', label: 'Главная', icon: 'pi pi-home', path: '/cabinet', permission: null },
  { id: 'catalog', label: 'Каталог', icon: 'pi pi-book', path: '/cabinet/catalog', permission: 'books:read' },
  { id: 'loans', label: 'Мои займы', icon: 'pi pi-bookmark', path: '/cabinet/loans', permission: 'loans:view' },
  { id: 'reservations', label: 'Бронирования', icon: 'pi pi-calendar', path: '/cabinet/reservations', permission: 'reservations:manage' }
]

/**
 * Получить данные текущего читателя
 * В реальности: переиспользуем /api/auth/me из authApi
 */
export async function fetchUserProfile() {
  // Этот эндпоинт уже реализован в authApi.js, можно импортировать оттуда:
  // import { fetchMeApi } from './authApi'
  // return await fetchMeApi()
  
  // Или делаем запрос напрямую:
  const response = await api.get('/auth/me')
  return response.data
}

/**
 * Выйти из системы
 * В реальности: POST /api/auth/logout
 */
export async function userLogout() {
  const response = await api.post('/auth/logout')
  return response.data
}

/**
 * Получить доступные пункты меню на основе прав пользователя
 * Фильтрация происходит на фронтенде после получения профиля
 */
export async function fetchUserMenuItems() {
  // Сначала получаем профиль, чтобы узнать права
  const profile = await fetchUserProfile()
  
  // Фильтруем меню: показываем пункт, если у него нет требования прав
  // ИЛИ если у пользователя есть нужное право
  return MENU_ITEMS.filter(item => 
    !item.permission || (profile.permissions && profile.permissions.includes(item.permission))
  )
}

/**
 * Получить статистику для личного кабинета
 * В реальности: GET /api/auth/user/stats
 */
export async function fetchUserStats() {
  const response = await api.get('/auth/user/stats')
  return response.data
}

/**
 * Утилита: проверить право доступа
 * Принимает массив прав пользователя и проверяемое право
 */
export function hasPermission(userPermissions, permission) {
  return userPermissions?.includes(permission) || false
}