// src/stores/adminStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as adminApi from '../api/adminApi'

export const useAdminStore = defineStore('admin', () => {
  // === STATE ===
  const users = ref([])
  const settings = ref(null)
  const genres = ref([])
  const locations = ref([])
  const auditLogs = ref([])
  const auditTotal = ref(0)
  const auditLoading = ref(false)
  const loading = ref(false)
  const error = ref(null)

  // === COMPUTED ===
  const totalUsers = computed(() => users.value.length)
  const activeUsers = computed(() => users.value.filter(u => u.status === 'active').length)
  const blockedUsers = computed(() => users.value.filter(u => u.status === 'blocked').length)
  const usersByRole = computed(() => {
    const roles = {}
    users.value.forEach(u => { roles[u.role] = (roles[u.role] || 0) + 1 })
    return roles
  })

  // === ACTIONS ===
  const loadUsers = async () => {
    loading.value = true
    error.value = null
    try {
      users.value = await adminApi.fetchUsersApi()
    } catch (e) { error.value = e.message }
    finally { loading.value = false }
  }

  const createUser = async (userData) => {
    try {
      const newUser = await adminApi.createUserApi(userData)
      users.value.push(newUser)
      return { success: true, data: newUser }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const updateUser = async (id, userData) => {
    try {
      const updated = await adminApi.updateUserApi(id, userData)
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) users.value[index] = updated
      return { success: true }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const deleteUser = async (id) => {
    try {
      await adminApi.deleteUserApi(id)
      users.value = users.value.filter(u => u.id !== id)
      return { success: true }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const toggleUserStatus = async (id) => {
    try {
      const updated = await adminApi.toggleUserStatusApi(id)
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) users.value[index] = updated
      return { success: true }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const loadSettings = async () => {
    loading.value = true
    error.value = null // Сбрасываем ошибку перед новым запросом
    try {
      // ИСПРАВЛЕНО: функция в adminApi.js называется fetchSettingsApi
      settings.value = await adminApi.fetchSettingsApi() 
    } catch (e) {
      error.value = e.message || 'Не удалось загрузить настройки'
    } finally {
      loading.value = false
    }
  }

  const saveSettings = async (newSettings) => {
    try {
      const updated = await adminApi.saveSettingsApi(newSettings)
      settings.value = updated
      return { success: true }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const loadGenres = async () => {
    loading.value = true
    error.value = null
    try {
      genres.value = await adminApi.fetchGenresApi()
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  const addGenre = async (name) => {
    try {
      const newGenre = await adminApi.addGenreApi(name)
      genres.value.push(newGenre)
      return { success: true, newGenre }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const updateGenre = async (id, { name }) => {
    try {
      const updated = await adminApi.updateGenreApi(id, { name })
      const index = genres.value.findIndex(g => g.id === id)
      if (index !== -1) genres.value[index] = updated
      return { success: true }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const deleteGenre = async (id) => {
    try {
      await adminApi.deleteGenreApi(id)
      genres.value = genres.value.filter(g => g.id !== id)
      return { success: true }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const loadLocations = async () => {
    try {
      // В adminApi.js нет fetchLocations, но этот метод пока не используется
      // locations.value = await adminApi.fetchLocations() 
    } catch (e) {
      error.value = e.message
    }
  }

  const loadAuditLogs = async ({ search = '', startDate = null, endDate = null, page = 1, limit = 20 } = {}) => {
    auditLoading.value = true
    error.value = null
    try {
      const response = await adminApi.fetchAuditLogsApi({
        search, startDate, endDate, page, limit
      })
      auditLogs.value = response.data
      auditTotal.value = response.total
    } catch (e) { error.value = e.message }
    finally { auditLoading.value = false }
  }

  // === INIT ===
  const init = async () => {
    await Promise.all([
      loadUsers(),
      loadSettings(),
      loadGenres(),
      // loadLocations(),
      loadAuditLogs()
    ])
  }

  return {
    // State
    users, settings, genres, locations, auditLogs, auditTotal, auditLoading, loading, error,
    // Computed
    totalUsers, activeUsers, blockedUsers, usersByRole,
    // Actions
    loadUsers, createUser, updateUser, deleteUser, toggleUserStatus,
    loadSettings, saveSettings,
    loadGenres, addGenre, updateGenre, deleteGenre,
    loadLocations,
    loadAuditLogs,
    init
  }
})