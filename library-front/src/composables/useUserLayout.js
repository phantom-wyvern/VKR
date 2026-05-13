// src/composables/useUserLayout.js
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { 
  fetchUserProfile, 
  fetchUserMenuItems, 
  userLogout,
  fetchUserStats 
} from '../api/userService'

export function useUserLayout() {
  const auth = useAuthStore()
  const menuItems = ref([])
  const stats = ref(null)
  const loading = ref(false)

  const userName = computed(() => auth.user?.name || 'Пользователь')
  const userRole = computed(() => auth.user?.role)

  const loadProfile = async () => {
    if (auth.user?.role !== 'reader') return
    
    loading.value = true
    try {
      // Подгружаем полные данные профиля, если их нет в сторе
      if (!auth.user?.permissions) {
        const profile = await fetchUserProfile()
        auth.setUser({ ...auth.user, ...profile })
      }
      // Загружаем меню и статистику параллельно
      const [menu, statsData] = await Promise.all([
        fetchUserMenuItems(),
        fetchUserStats()
      ])
      menuItems.value = menu
      stats.value = statsData
    } catch (e) {
      console.error('Failed to load user profile:', e)
    } finally {
      loading.value = false
    }
  }

  const handleLogout = async () => {
    loading.value = true
    try {
      await userLogout()
      auth.logout()
    } catch (e) {
      console.error('Logout error:', e)
      auth.logout() // Всё равно выходим при ошибке
    }
  }

  const checkPermission = (permission) => {
    return auth.user?.permissions?.includes(permission) || false
  }

  const refreshStats = async () => {
    try {
      stats.value = await fetchUserStats()
    } catch (e) {
      console.error('Failed to refresh stats:', e)
    }
  }

  onMounted(() => {
    if (auth.isAuthenticated && auth.user?.role === 'reader') {
      loadProfile()
    }
  })

  return {
    userName,
    userRole,
    menuItems,
    stats,
    loading,
    handleLogout,
    checkPermission,
    loadProfile,
    refreshStats
  }
}