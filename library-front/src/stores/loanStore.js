// src/stores/loanStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './authStore'
import * as loanApi from '../api/loanApi'

export const useLoanStore = defineStore('loans', () => {
  const auth = useAuthStore()
  
  // === STATE ===
  const activeLoans = ref([])
  const reservations = ref([])
  const history = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // Пагинация для истории
  const historyPagination = ref({
    page: 1,
    limit: 10,
    total: 0
  })

  // === COMPUTED ===
  const stats = computed(() => loanApi.computeLoanStats(activeLoans.value))
  
  const overdueCount = computed(() => stats.value.overdueCount)
  const totalFineAmount = computed(() => stats.value.totalFineAmount)
  const nextDueDate = computed(() => stats.value.nextDueDate)
  
  const readyReservations = computed(() => 
    reservations.value.filter(r => r.status === 'ready')
  )

  // === ACTIONS ===

  const loadActiveLoans = async () => {
    if (!auth.user?.id) return
    
    loading.value = true
    error.value = null
    try {
      activeLoans.value = await loanApi.fetchActiveLoansApi(auth.user.id)
    } catch (e) {
      error.value = e.message
      console.error('Failed to load active loans:', e)
    } finally {
      loading.value = false
    }
  }

  const loadHistory = async ({ page = 1 } = {}) => {
    if (!auth.user?.id) return
    
    loading.value = true
    try {
      const response = await loanApi.fetchLoanHistoryApi({
        page,
        limit: historyPagination.value.limit
      })
      history.value = response.data
      historyPagination.value.total = response.total
      historyPagination.value.page = page
    } catch (e) {
      error.value = e.message
      console.error('Failed to load history:', e)
    } finally {
      loading.value = false
    }
  }

  const loadReservations = async () => {
    if (!auth.user?.id) return
    
    loading.value = true
    try {
      reservations.value = await loanApi.fetchReservationsApi()
    } catch (e) {
      error.value = e.message
      console.error('Failed to load reservations:', e)
    } finally {
      loading.value = false
    }
  }

  const renewLoan = async (loanId) => {
    try {
      const result = await loanApi.renewLoanApi(loanId)
      // Обновляем локальный кэш
      const index = activeLoans.value.findIndex(l => l.id === loanId)
      if (index !== -1) {
        activeLoans.value[index].dueDate = result.newDueDate
        activeLoans.value[index].renewalsCount = result.renewalsCount
      }
      return { success: true, message: result.message }
    } catch (e) {
      error.value = e.message
      return { success: false, message: e.message }
    }
  }

  const cancelReservation = async (resId) => {
    try {
      await loanApi.cancelReservationApi(resId)
      reservations.value = reservations.value.filter(r => r.id !== resId)
      return { success: true, message: 'Бронирование отменено' }
    } catch (e) {
      error.value = e.message
      return { success: false, message: e.message }
    }
  }

  const requestReturn = async (loanId) => {
    try {
      const result = await loanApi.requestReturnApi(loanId)
      // Помечаем как "возврат запрошен" (опционально)
      const index = activeLoans.value.findIndex(l => l.id === loanId)
      if (index !== -1) {
        activeLoans.value[index].status = 'return_requested'
      }
      return result
    } catch (e) {
      error.value = e.message
      return { success: false, message: e.message }
    }
  }

  const claimReservation = async (resId) => {
    try {
      const result = await loanApi.claimReservationApi(resId)
      const index = reservations.value.findIndex(r => r.id === resId)
      if (index !== -1) {
        reservations.value[index].status = 'fulfilled'
      }
      return result
    } catch (e) {
      error.value = e.message
      return { success: false, message: e.message }
    }
  }

  const rateBook = async ({ loanId, rating, comment }) => {
    try {
      const result = await loanApi.rateBookApi({ loanId, rating, comment })
      // Обновляем историю
      const index = history.value.findIndex(h => h.id === loanId)
      if (index !== -1) {
        history.value[index].rating = rating
        history.value[index].comment = comment
      }
      return result
    } catch (e) {
      error.value = e.message
      return { success: false, message: e.message }
    }
  }

  const clearError = () => { error.value = null }

  // === INIT ===
  const init = async () => {
    if (!auth.isAuthenticated) return
    
    await Promise.all([
      loadActiveLoans(),
      loadReservations()
      // history грузим по запросу, т.к. может быть большой
    ])
  }

  return {
    // State
    activeLoans, reservations, history, loading, error, historyPagination,
    // Computed
    stats, overdueCount, totalFineAmount, nextDueDate, readyReservations,
    // Actions
    loadActiveLoans, loadHistory, loadReservations,
    renewLoan, cancelReservation, requestReturn, claimReservation, rateBook,
    clearError, init
  }
})