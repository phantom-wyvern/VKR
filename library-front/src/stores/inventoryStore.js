import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as inventoryApi from '../api/inventoryApi'
import api from '../api/client'

export const useInventoryStore = defineStore('inventory', () => {
  const books = ref([])
  const fines = ref([])
  const reservations = ref([])
  const activeLoans = ref([])
  const loading = ref(false)
  const error = ref(null)

  const stats = computed(() => inventoryApi.computeInventoryStats(books.value))
  const finesStats = computed(() => inventoryApi.computeFinesStats(fines.value))
  const totalBooks = computed(() => stats.value.totalBooks)
  const totalCopies = computed(() => stats.value.totalCopies)
  const availableCopies = computed(() => stats.value.availableCopies)
  const unpaidFines = computed(() => finesStats.value.unpaidFines)
  const totalUnpaidAmount = computed(() => finesStats.value.totalUnpaidAmount)

  const loadActiveLoans = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/inventory/loans/active')
      activeLoans.value = response.data?.data || []
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      console.error('Failed to load active loans:', e)
    } finally {
      loading.value = false
    }
  }

  const loadBooks = async () => {
    loading.value = true
    error.value = null
    try {
      books.value = await inventoryApi.fetchBooksApi()
    } catch (e) { 
      error.value = e.message 
    } finally { 
      loading.value = false 
    }
  }

  const addBook = async (bookData) => {
    try {
      const newBook = await inventoryApi.addBookApi(bookData)
      books.value.push(newBook)
      return { success: true, newBook }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const updateBook = async (id, bookData) => {
    try {
      const updated = await inventoryApi.updateBookApi(id, bookData)
      const index = books.value.findIndex(b => b.id === id)
      if (index !== -1) books.value[index] = updated
      return { success: true }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const deleteBook = async (id) => {
    try {
      await inventoryApi.deleteBookApi(id)
      books.value = books.value.filter(b => b.id !== id)
      return { success: true }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const loadFines = async () => {
    loading.value = true
    try { 
      fines.value = await inventoryApi.fetchFinesApi() 
    } catch (e) { 
      error.value = e.message 
    } finally { 
      loading.value = false 
    }
  }

  const markFineAsPaid = async (fineId) => {
    try {
      const updated = await inventoryApi.markFineAsPaidApi(fineId)
      const index = fines.value.findIndex(f => f.id === fineId)
      if (index !== -1) fines.value[index] = updated
      return { success: true }
    } catch (e) {
      error.value = e.message
      return { success: false, error: e.message }
    }
  }

  const loadReservations = async () => {
    loading.value = true
    error.value = null
    try { 
      reservations.value = await inventoryApi.fetchReservationsApi() 
    } catch (e) { 
      error.value = e.message 
    } finally { 
      loading.value = false 
    }
  }

  const approveReservation = async (resId) => {
    try {
      await inventoryApi.approveReservationApi(resId)
      const index = reservations.value.findIndex(r => r.id === resId)
      if (index !== -1) reservations.value[index].status = 'ready'
      return { success: true, message: 'Бронирование подтверждено' }
    } catch (e) {
      error.value = e.message
      return { success: false, message: e.response?.data?.detail || e.message }
    }
  }

  const cancelReservation = async (resId) => {
    try {
      await inventoryApi.cancelReservationApi(resId)
      const index = reservations.value.findIndex(r => r.id === resId)
      if (index !== -1) reservations.value[index].status = 'cancelled'
      return { success: true, message: 'Бронирование отменено' }
    } catch (e) {
      error.value = e.message
      return { success: false, message: e.response?.data?.detail || e.message }
    }
  }

  const fulfillReservation = async (resId) => {
    try {
      await inventoryApi.fulfillReservationApi(resId)
      const index = reservations.value.findIndex(r => r.id === resId)
      if (index !== -1) reservations.value[index].status = 'fulfilled'
      return { success: true, message: 'Бронирование выполнено' }
    } catch (e) {
      error.value = e.message
      return { success: false, message: e.response?.data?.detail || e.message }
    }
  }

  const checkoutBook = async ({ copyId, userId, userName, reservationId }) => {
    try {
      const result = await inventoryApi.checkoutBookApi({ copyId, userId, userName, reservationId })
      // После выдачи обновляем статус копии и загружаем актуальные данные
      await loadBooks()
      return result
    } catch (e) {
      error.value = e.message
      return { success: false, message: e.response?.data?.detail || e.message }
    }
  }

  const returnBook = async (copyId) => {
    try {
      const result = await inventoryApi.returnBookApi(copyId)
      // Обновляем статус копии локально
      for (const book of books.value) {
        const copy = book.copies?.find(c => c.id === copyId)
        if (copy) { copy.status = 'available'; break }
      }
      // Убираем из активных займов
      activeLoans.value = activeLoans.value.filter(l => l.copyId !== copyId)
      return { success: true, message: result.message || 'Книга возвращена' }
    } catch (e) {
      error.value = e.message
      return { success: false, message: e.response?.data?.detail || e.message }
    }
  }

  const init = async () => {
    loading.value = true
    error.value = null
    try {
      await Promise.all([loadBooks(), loadActiveLoans(), loadReservations()])
    } catch (e) {
      error.value = e.message
    } finally { 
      loading.value = false 
    }
  }

  return {
    activeLoans, books, fines, reservations, loading, error,
    totalBooks, totalCopies, availableCopies, unpaidFines, totalUnpaidAmount,
    init, loadActiveLoans, loadBooks, addBook, updateBook, deleteBook,
    loadFines, markFineAsPaid, loadReservations, approveReservation, cancelReservation, fulfillReservation,
    checkoutBook, returnBook
  }
})