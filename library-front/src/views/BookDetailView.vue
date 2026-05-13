<template>
  <!-- Loading State -->
  <div v-if="loading" class="min-h-[60vh] flex items-center justify-center">
    <div class="text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка информации о книге...</p>
    </div>
  </div>

  <!-- Error State -->
  <div v-else-if="error" class="min-h-[60vh] flex items-center justify-center">
    <div class="glass p-8 text-center max-w-md w-full border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ error }}</p>
      <div class="flex gap-3 justify-center">
        <Button label="Назад" icon="pi pi-arrow-left" class="p-button-outlined" @click="$router.back()" />
        <Button label="Повторить" icon="pi pi-refresh" @click="loadBook" />
      </div>
    </div>
  </div>

  <!-- Book Detail -->
  <div v-else-if="book" class="animate-fade-in book-detail-wrapper">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6 flex-wrap gap-4">
      <Button
        :label="isInCabinet ? 'Назад к каталогу' : 'Назад к каталогу'"
        :icon="isInCabinet ? 'pi pi-arrow-left' : 'pi pi-arrow-left'"
        class="p-button-text p-button-sm"
        @click="goBack"
      />
      <h1 class="page-title mb-0">{{ book.title }}</h1>
    </div>

    <div class="book-grid">
      <!-- Card 1: Info -->
      <div class="glass settings-card">
        <h3 class="card-header">
          <i class="pi pi-info-circle"></i> Основная информация
        </h3>
        <div class="card-body">
          <div class="setting-row">
            <span class="setting-label">Автор</span>
            <span class="setting-value">{{ book.author }}</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">Год издания</span>
            <span class="setting-value">{{ book.year }}</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">Жанр</span>
            <span class="setting-value">{{ book.genre }}</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">ISBN</span>
            <span class="setting-value font-mono">{{ book.isbn }}</span>
          </div>
          <div class="setting-row">
            <span class="setting-label">Статус</span>
            <Tag :value="bookStatus.label" :severity="bookStatus.class" />
          </div>
        </div>
      </div>

      <!-- Card 2: Cover & Actions -->
      <div class="glass settings-card cover-card">
        <h3 class="card-header">
          <i class="pi pi-image"></i> Обложка
        </h3>
        <div class="card-body text-center">
          <div class="mb-4 mx-auto cover-wrapper">
            <div class="aspect-ratio-wrapper rounded-xl overflow-hidden shadow-lg bg-surface-2">
              <img 
                :src="book.cover" 
                :alt="`Обложка книги ${book.title}`" 
                class="cover-image"
                @error="e => e.target.src = FALLBACK_COVER" 
              />
            </div>
          </div>
          <div class="flex flex-col gap-3">
            <Button
              v-if="isAlreadyReserved"
              label="Уже забронировано"
              icon="pi pi-check-circle"
              class="w-full p-button-success"
              disabled
            />
            <Button
              v-else
              :label="!isAvailable ? 'Нет в наличии' : 'Забронировать'"
              icon="pi pi-bookmark"
              class="w-full"
              :loading="reserving"
              :disabled="!isAvailable || reserving"
              @click="handleReserve"
            />
            <Button label="Поделиться" icon="pi pi-share-alt" class="p-button-outlined w-full" @click="shareBook" />
          </div>
        </div>
      </div>

      <!-- Card 3: Description -->
      <div class="glass settings-card full-width">
        <h3 class="card-header">
          <i class="pi pi-align-left"></i> Описание
        </h3>
        <div class="card-body">
          <p class="text-secondary leading-relaxed">{{ book.description || 'Описание отсутствует.' }}</p>
        </div>
      </div>

      <!-- Card 4: Copies -->
      <div class="glass settings-card full-width">
        <h3 class="card-header">
          <i class="pi pi-map-marker"></i> Наличие в библиотеке
        </h3>
        <div class="card-body" style="padding: 0;">
          <DataTable 
            :value="book.copies" 
            stripedRows 
            class="border-none"
            emptyMessage="Информация об экземплярах отсутствует"
          >
            <Column field="id" header="ID экземпляра" style="width: 150px"></Column>
            <Column field="location" header="Расположение"></Column>
            <Column header="Статус" style="width: 150px">
              <template #body="{ data }">
                <Tag :value="data.status === 'available' ? 'В наличии' : 'Выдан'" 
                     :severity="data.status === 'available' ? 'success' : 'danger'" />
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
    </div>
  </div>

</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookStore } from '../stores/bookStore'
import { useLoanStore } from '../stores/loanStore'
import { useAuthStore } from '../stores/authStore'
import { useToast } from 'primevue/usetoast'
import { FALLBACK_COVER } from '../config/constants'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'

const route = useRoute()
const router = useRouter()
const bookStore = useBookStore()
const loanStore = useLoanStore()
const authStore = useAuthStore()
const toast = useToast()

const book = ref(null)
const loading = ref(false)
const error = ref(null)
const reserving = ref(false)

// Вычисляемые свойства
const isInCabinet = computed(() => route.path.startsWith('/cabinet'))

const isAlreadyReserved = computed(() => {
  // Проверяем через loanStore, есть ли уже активная бронь у читателя на эту книгу
  if (!loanStore.reservations.length || !book.value?.id) return false
  return loanStore.reservations.some(
    r => r.bookId === book.value.id && ['pending', 'ready'].includes(r.status)
  )
})

const isAvailable = computed(() => book.value?.copies?.some(c => c.status === 'available') ?? false)

const bookStatus = computed(() => {
  if (!book.value?.copies?.length) return { label: 'Неизвестно', class: 'secondary' }
  const available = book.value.copies.filter(c => c.status === 'available').length
  const total = book.value.copies.length
  if (available === total) return { label: 'В наличии', class: 'success' }
  if (available === 0) return { label: 'Нет в наличии', class: 'danger' }
  return { label: `Мало (${available}/${total})`, class: 'warning' }
})

// Загрузка книги
const loadBook = async () => {
  const id = route.params.id
  if (!id) {
    error.value = 'ID книги не указан'
    return
  }

  loading.value = true
  error.value = null
  try {
    book.value = await bookStore.loadBookDetails(id)
  } catch (e) {
    error.value = e.message || 'Не удалось загрузить книгу'
    console.error('Book detail load error:', e)
  } finally {
    loading.value = false
  }
}

// Навигация назад
const goBack = () => {
  if (isInCabinet.value) {
    router.push('/cabinet/catalog')
  } else {
    router.push('/catalog')
  }
}

// Бронирование
const handleReserve = async () => {
  if (!authStore.isAuthenticated) {
    toast.add({ severity: 'warn', summary: 'Требуется вход', detail: 'Войдите в систему, чтобы забронировать книгу', life: 3000 })
    router.push(`/login?redirect=${route.fullPath}`)
    return
  }

  if (!isAvailable.value) {
    toast.add({ severity: 'warn', summary: 'Недоступно', detail: 'Свободных экземпляров нет', life: 3000 })
    return
  }

  reserving.value = true
  try {
    const result = await bookStore.reserveBook({
      bookId: book.value.id
    })

    if (result.success) {
      toast.add({
        severity: 'success',
        summary: 'Успешно',
        detail: result.message || `Книга "${book.value.title}" забронирована. Ожидайте уведомления.`,
        life: 4000
      })
      // Обновляем бронирования и данные книги
      await Promise.all([
        loanStore.loadReservations(),
        loadBook()
      ])
    }
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.message || 'Не удалось оформить бронь'
    toast.add({ severity: 'error', summary: 'Ошибка', detail: errorMsg, life: 5000 })
  } finally {
    reserving.value = false
  }
}

// Поделиться
const shareBook = () => {
  const url = `${window.location.origin}${route.fullPath}`
  if (navigator.share) {
    navigator.share({ title: book.value.title, url })
  } else {
    navigator.clipboard.writeText(url).then(() => {
      toast.add({ severity: 'success', summary: 'Скопировано', detail: 'Ссылка на книгу скопирована в буфер обмена', life: 2000 })
    })
  }
}

// Инициализация и отслеживание изменения ID в URL
onMounted(async () => {
  // Загружаем бронирования, чтобы корректно определить isAlreadyReserved
  if (authStore.isAuthenticated && authStore.user?.role === 'reader') {
    await loanStore.loadReservations()
  }
  loadBook()
})
watch(() => route.params.id, () => loadBook())
</script>

<style scoped>
.book-detail-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 48px;
  width: 100%;
}

.book-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
}

.cover-card {
  padding: 20px;
}

.cover-wrapper {
  max-width: 200px;
}

.aspect-ratio-wrapper {
  aspect-ratio: 2 / 3;
  width: 100%;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.cover-image:hover {
  transform: scale(1.03);
}

.full-width {
  grid-column: 1 / -1;
}

@media (max-width: 900px) {
  .book-grid {
    grid-template-columns: 1fr;
  }
  .cover-card {
    order: -1;
    max-width: 320px;
    margin: 0 auto 24px;
    width: 100%;
  }
  .cover-wrapper {
    max-width: 180px;
  }
}
</style>