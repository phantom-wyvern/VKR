import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '../router'
import { loginApi, logoutApi, fetchMeApi, registerApi } from '../api/authApi'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token') || null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const hasRole = (role) => user.value?.role === role
  const hasPermission = (permission) => user.value?.permissions?.includes(permission) || false

  const login = async (credentials) => {
    loading.value = true
    error.value = null
    try {
      const response = await loginApi(credentials)
      token.value = response.token
      user.value = response.user
      localStorage.setItem('auth_token', response.token)

      const redirect = router.currentRoute.value.query.redirect
      if (response.user.role === 'librarian') router.push('/librarian')
      else if (response.user.role === 'admin') router.push('/admin')
      else router.push(redirect || '/cabinet')

      return { success: true, user: response.user }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally { loading.value = false }
  }

  const register = async (userData) => {
    loading.value = true
    error.value = null
    try {
      await registerApi(userData)
      return { success: true }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally { loading.value = false }
  }

  const logout = async () => {
    loading.value = true
    try {
      if (token.value) await logoutApi(token.value)
    } catch (err) {
      console.error('Logout API error:', err)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
      router.push('/login')
      loading.value = false
    }
  }

  const init = async () => {
    if (!token.value) return false
    loading.value = true
    try {
      const userData = await fetchMeApi(token.value)
      user.value = userData
      return true
    } catch (err) {
      console.warn('Session invalid:', err.message)
      token.value = null
      localStorage.removeItem('auth_token')
      return false
    } finally { loading.value = false }
  }

  const clearError = () => { error.value = null }
  const setUser = (userData) => { user.value = userData }

  return {
    user, token, loading, error,
    isAuthenticated, hasRole, hasPermission,
    login, register, logout, init, clearError, setUser
  }
})