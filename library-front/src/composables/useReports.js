// src/composables/useReports.js
import { ref, computed } from 'vue'
import * as reportsApi from '../api/reportsApi'

export function useReports() {
  const loading = ref(false)
  const error = ref(null)
  
  // Данные графиков
  const loansChart = ref(null)
  const activityChart = ref(null)
  const genresChart = ref(null)
  const topBooks = ref([])
  const stats = ref(null)
  
  // Фильтры
  const filters = ref({
    reportType: 'all',
    period: 'month',
    dateFrom: null,
    dateTo: null
  })

  const loadReports = async () => {
    loading.value = true
    error.value = null
    
    try {
      const { reportType, period, dateFrom, dateTo } = filters.value
      
      // Загружаем только нужные данные в зависимости от типа отчёта
      const promises = []
      
      if (reportType === 'loans' || reportType === 'all') {
        promises.push(
          reportsApi.fetchLoansByMonthApi({ period, startDate: dateFrom, endDate: dateTo })
            .then(data => loansChart.value = data)
        )
      }
      
      if (reportType === 'activity' || reportType === 'all') {
        promises.push(
          reportsApi.fetchActivityByDayApi()
            .then(data => activityChart.value = data)
        )
      }
      
      if (reportType === 'genres' || reportType === 'all') {
        promises.push(
          reportsApi.fetchGenresDistributionApi()
            .then(data => genresChart.value = data)
        )
      }
      
      if (reportType === 'top' || reportType === 'all') {
        promises.push(
          reportsApi.fetchTopBooksApi({ limit: 5, period })
            .then(data => topBooks.value = data)
        )
      }
      
      // Статистика грузится всегда
      promises.push(
        reportsApi.fetchReportsStatsApi()
          .then(data => stats.value = data)
      )
      
      await Promise.all(promises)
      return { success: true }
      
    } catch (e) {
      error.value = e.message
      console.error('Failed to load reports:', e)
      return { success: false, error: e.message }
    } finally {
      loading.value = false
    }
  }

  const resetFilters = () => {
    filters.value = {
      reportType: 'all',
      period: 'month',
      dateFrom: null,
      dateTo: null
    }
  }

  const setFilter = (key, value) => {
    filters.value[key] = value
  }

  return {
    loading,
    error,
    filters,
    loansChart,
    activityChart,
    genresChart,
    topBooks,
    stats,
    loadReports,
    resetFilters,
    setFilter
  }
}