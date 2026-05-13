// src/composables/useBook.js
import { ref, computed } from 'vue'
import { fetchBookById, computeBookStatus } from '../api/bookService'

export function useBook(initialBook = null) {
  const book = ref(initialBook)
  const loading = ref(false)
  const error = ref(null)

  const status = computed(() => 
    book.value ? computeBookStatus(book.value) : null
  )

  const loadBook = async (id) => {
    loading.value = true
    error.value = null
    try {
      book.value = await fetchBookById(id)
    } catch (e) {
      error.value = e.message
      console.error('Failed to load book:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    book,
    loading,
    error,
    status,
    loadBook
  }
}