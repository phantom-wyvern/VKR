// src/api/adminService.js

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))

// Моковые данные
const MOCK_ADMIN_USER = {
  id: 999,
  name: 'Александр Админов',
  email: 'admin@library.ru',
  role: 'admin',
  avatar: null,
  permissions: ['users:manage', 'settings:edit', 'audit:view', 'genres:manage']
}

const MOCK_MENU_ITEMS = [
  { id: 'dashboard', label: 'Обзор', icon: 'pi pi-chart-bar', path: '/admin', permission: null },
  { id: 'users', label: 'Пользователи', icon: 'pi pi-users', path: '/admin/users', permission: 'users:manage' },
  { id: 'settings', label: 'Настройки', icon: 'pi pi-cog', path: '/admin/settings', permission: 'settings:edit' },
  { id: 'genres', label: 'Жанры', icon: 'pi pi-tags', path: '/admin/genres', permission: 'genres:manage' },
  { id: 'audit', label: 'Аудит', icon: 'pi pi-history', path: '/admin/audit', permission: 'audit:view' }
]

/**
 * Получить данные текущего администратора
 */
export async function fetchAdminProfile() {
  await delay(250)
  // В реальности: GET /api/admin/me
  return { ...MOCK_ADMIN_USER }
}

/**
 * Выйти из системы
 */
export async function adminLogout() {
  await delay(200)
  // В реальности: POST /api/auth/logout с токеном
  return { success: true, message: 'Выход выполнен' }
}

/**
 * Получить доступные пункты меню на основе прав
 */
export async function fetchAdminMenuItems() {
  await delay(150)
  // В реальности: GET /api/admin/menu
  // Фильтруем по моковым пермишенам
  const userPerms = MOCK_ADMIN_USER.permissions
  return MOCK_MENU_ITEMS.filter(item => 
    !item.permission || userPerms.includes(item.permission)
  )
}

/**
 * Проверить право доступа
 */
export function hasPermission(permission) {
  // В реальности можно кэшировать или проверять на бэкенде
  return MOCK_ADMIN_USER.permissions.includes(permission)
}