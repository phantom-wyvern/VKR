// src/composables/useLibrarianLayout.js
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { 
  fetchLibrarianProfile, 
  fetchLibrarianMenuItems, 
  librarianLogout,
  fetchLibrarianStats 
} from '../api/librarianService'

export function useLibrarianLayout() {
  const auth = useAuthStore()
  const menuItems = ref([])
  const stats = ref(null)
  const loading = ref(false)

  const userName = computed(() => auth.user?.name || 'Загрузка...')
  const userRole = computed(() => auth.user?.role)

  const loadProfile = async () => {
    if (auth.user?.role !== 'librarian') return
    
    loading.value = true
    try {
      // Подгружаем полные данные профиля, если их нет в сторе
      if (!auth.user?.permissions) {
        const profile = await fetchLibrarianProfile()
        auth.setUser({ ...auth.user, ...profile })
      }
      // Загружаем меню и статистику параллельно
      const [menu, statsData] = await Promise.all([
        fetchLibrarianMenuItems(),
        fetchLibrarianStats()
      ])
      menuItems.value = menu
      stats.value = statsData
    } catch (e) {
      console.error('Failed to load librarian profile:', e)
    } finally {
      loading.value = false
    }
  }

  const handleLogout = async () => {
    loading.value = true
    try {
      await librarianLogout()
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
      stats.value = await fetchLibrarianStats()
    } catch (e) {
      console.error('Failed to refresh stats:', e)
    }
  }

  onMounted(() => {
    if (auth.isAuthenticated && auth.user?.role === 'librarian') {
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