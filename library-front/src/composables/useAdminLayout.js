import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { fetchSettingsApi, fetchGenresApi, fetchAuditLogsApi } from '../api/adminApi'
import { fetchMeApi, logoutApi } from '../api/authApi'

export function useAdminLayout() {
  const auth = useAuthStore()
  const menuItems = ref([])
  const loading = ref(false)
  const userName = computed(() => auth.user?.name || 'Загрузка...')
  const userRole = computed(() => auth.user?.role)

  const loadProfile = async () => {
    if (auth.user?.role !== 'admin') return
    loading.value = true
    try {
      // 1. Обновляем профиль, если нет прав в сторе (реальный запрос)
      if (!auth.user?.permissions) {
        const profile = await fetchMeApi()
        auth.setUser({ ...auth.user, ...profile })
      }

      // 2. Загружаем админ-данные из реального API
      await Promise.all([
        fetchSettingsApi(),
        fetchGenresApi(),
        fetchAuditLogsApi({ limit: 5 })
      ])

      // 3. Формируем меню на основе доступных модулей (раньше было в моках)
      menuItems.value = [
        { id: 'dashboard', label: 'Обзор', icon: 'pi pi-chart-bar', path: '/admin' },
        { id: 'users', label: 'Пользователи', icon: 'pi pi-users', path: '/admin/users', permission: 'users:manage' },
        { id: 'settings', label: 'Настройки', icon: 'pi pi-cog', path: '/admin/settings', permission: 'settings:edit' },
        { id: 'genres', label: 'Жанры', icon: 'pi pi-tags', path: '/admin/genres', permission: 'genres:manage' },
        { id: 'audit', label: 'Аудит', icon: 'pi pi-history', path: '/admin/audit', permission: 'audit:view' }
      ]
    } catch (e) {
      console.error('Failed to load admin profile:', e)
    } finally {
      loading.value = false
    }
  }

  const handleLogout = async () => {
    loading.value = true
    try {
      await logoutApi() // Реальный запрос к /api/auth/logout
      auth.logout()
    } catch (e) {
      console.error('Logout error:', e)
      auth.logout()
    }
  }

  const checkPermission = (permission) => {
    return auth.user?.permissions?.includes(permission) || false
  }

  onMounted(() => {
    if (auth.isAuthenticated && auth.user?.role === 'admin') {
      loadProfile()
    }
  })

  return {
    userName,
    userRole,
    menuItems,
    loading,
    handleLogout,
    checkPermission,
    loadProfile
  }
}