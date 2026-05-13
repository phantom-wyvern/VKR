// src/stores/bookStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as bookApi from '../api/bookApi'

export const useBookStore = defineStore('books', () => {
  // === STATE ===
  const books = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // Пагинация
  const pagination = ref({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0
  })
  
  // Фильтры
  const filters = ref({
    search: '',
    genre: '',
    year: '',
    status: ''
  })

  // === COMPUTED ===
  
  const filteredBooks = computed(() => books.value)
  
  const genres = ref([])
  const years = ref([])
  
  const statuses = [
    { label: 'Все', value: '' },
    { label: 'В наличии', value: 'available' },
    { label: 'Все выданы', value: 'borrowed' }
  ]

  // === ACTIONS ===

  const loadBooks = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await bookApi.fetchBooksApi({
        ...filters.value,
        page: pagination.value.page,
        limit: pagination.value.limit
      })
      books.value = response.data
      pagination.value.total = response.total
      pagination.value.totalPages = response.totalPages
    } catch (e) {
      error.value = e.message
      console.error('Failed to load books:', e)
    } finally {
      loading.value = false
    }
  }

  const loadBookDetails = async (id) => {
    loading.value = true
    error.value = null
    try {
      return await bookApi.fetchBookByIdApi(id)
    } catch (e) {
      error.value = e.message
      console.error('Failed to load book:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  const loadFilters = async () => {
    try {
      const [genresData, yearsData] = await Promise.all([
        bookApi.fetchGenresApi(),
        bookApi.fetchYearsApi()
      ])
      genres.value = genresData
      years.value = yearsData
    } catch (e) {
      console.error('Failed to load filters:', e)
    }
  }

  const applyFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
    pagination.value.page = 1 // Сброс на первую страницу при новом фильтре
    return loadBooks()
  }

  const resetFilters = () => {
    filters.value = { search: '', genre: '', year: '', status: '' }
    pagination.value.page = 1
    return loadBooks()
  }

  const setPage = (page) => {
    pagination.value.page = page
    return loadBooks()
  }

  const reserveBook = async ({ bookId }) => {
    try {
      const result = await bookApi.reserveBookApi({ bookId })
      return result
    } catch (e) {
      // Пробрасываем ошибку целиком для обработки на уровне UI
      throw e
    }
  }

  const getBookStatus = (book) => {
    return bookApi.computeBookStatus(book.copies)
  }

  const getBookById = (id) => {
    return books.value.find(b => b.id === Number(id))
  }

  // === INIT ===
  const init = async () => {
    await Promise.all([
      loadFilters(),
      loadBooks()
    ])
  }

  return {
    // State
    books, loading, error, filters, pagination,
    // Computed
    filteredBooks, genres, years, statuses,
    // Actions
    loadBooks, loadBookDetails, loadFilters,
    applyFilters, resetFilters, setPage,
    reserveBook, getBookStatus, getBookById,
    init
  }
})