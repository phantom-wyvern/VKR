<template>
  <div class="animate-fade-in catalog-wrapper">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="page-title">
          <i class="pi pi-book" style="color: var(--primary);"></i>
          Каталог книг
        </h1>
        <p class="page-subtitle">Поиск и фильтрация книг в библиотеке</p>
      </div>
      <Button 
        icon="pi pi-refresh" 
        class="p-button-outlined p-button-sm"
        :loading="store.loading"
        @click="refreshCatalog"
        title="Обновить каталог"
      />
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar glass mb-8">
      <div class="filter-item">
        <label class="filter-label">Поиск</label>
        <InputText v-model="store.filters.search" placeholder="Название или автор" class="w-full" @keyup.enter="applyFilters" />
      </div>
      
      <div class="filter-item">
        <label class="filter-label">Жанр</label>
        <Dropdown v-model="store.filters.genre" :options="genreOptions" placeholder="Все жанры" class="w-full" @change="applyFilters" />
      </div>
      
      <div class="filter-item">
        <label class="filter-label">Год</label>
        <Dropdown v-model="store.filters.year" :options="yearOptions" placeholder="Все годы" class="w-full" @change="applyFilters" />
      </div>
      
      <div class="filter-item">
        <label class="filter-label">Статус</label>
        <Dropdown v-model="store.filters.status" :options="store.statuses" optionLabel="label" optionValue="value" placeholder="Все статусы" class="w-full" @change="applyFilters" />
      </div>

      <div class="filter-actions-group">
        <Button label="Сбросить" icon="pi pi-undo" class="p-button-outlined p-button-sm" @click="resetFilters" :disabled="store.loading" />
        <Button label="Применить" icon="pi pi-filter" :loading="store.loading" @click="applyFilters" />
        <span class="results-count">Найдено: <strong>{{ store.pagination?.total ?? store.filteredBooks?.length ?? 0 }}</strong></span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading && !store.books?.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка каталога...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ store.error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="refreshCatalog" />
    </div>

    <!-- Table -->
    <template v-else>
      <div class="table-container">
        <DataTable 
          :value="store.books"
          :loading="store.loading"
          stripedRows
          responsiveLayout="scroll"
          paginator
          :rows="10"
          :totalRecords="store.pagination?.total"
          :lazy="true"
          @page="onPageChange"
          class="border-none"
          emptyMessage="Книги не найдены"
        >
          <Column header="Обложка" style="width: 80px">
            <template #body="{ data }">
              <div class="cover-thumb">
                <img :src="data.cover || fallbackCover" :alt="data.title" @error="e => e.target.src = fallbackCover" />
              </div>
            </template>
          </Column>

          <Column field="title" header="Название" sortable>
            <template #body="{ data }">
              <router-link :to="getBookRoute(data.id)" class="book-title-link">
                {{ data.title }}
              </router-link>
            </template>
          </Column>

          <Column field="author" header="Автор" sortable></Column>
          <Column field="year" header="Год" sortable style="width: 80px"></Column>
          <Column field="genre" header="Жанр" sortable></Column>

          <Column header="Статус" style="width: 140px">
            <template #body="{ data }">
              <Tag :value="getBookStatusText(data)" :severity="getBookStatusSeverity(data)" />
            </template>
          </Column>

          <Column header="Действия" style="width: 200px">
            <template #body="{ data }">
              <div class="action-buttons">
                <router-link :to="getBookRoute(data.id)">
                  <Button label="Подробнее" icon="pi pi-eye" class="p-button-sm p-button-outlined" />
                </router-link>
                <Button
                  v-if="isReader && isBookAvailable(data)"
                  label="Забронировать"
                  icon="pi pi-bookmark"
                  class="p-button-sm"
                  :loading="reservingBook === data.id"
                  @click="handleQuickReserve(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookStore } from '../stores/bookStore'
import { useAuthStore } from '../stores/authStore'
import { useToast } from 'primevue/usetoast'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'

const route = useRoute()
const router = useRouter()
const store = useBookStore()
const toast = useToast()
const authStore = useAuthStore()
const fallbackCover = 'https://placehold.co/200x300/e2e8f0/64748b?text=Нет+обложки'

const isInCabinet = computed(() => route.path.startsWith('/cabinet'))
const isReader = computed(() => authStore.user?.role === 'reader')
const reservingBook = ref(null)

const genreOptions = computed(() => store.genres.map(g => ({ label: g, value: g })))
const yearOptions = computed(() => store.years.map(y => ({ label: String(y), value: y })))

onMounted(() => { refreshCatalog() })

const getBookRoute = (bookId) => {
  if (isInCabinet.value) {
    return { name: 'reader-book-detail', params: { id: bookId } }
  } else {
    return { name: 'book-detail', params: { id: bookId } }
  }
}

const isBookAvailable = (book) => {
  if (!book?.copies?.length) return false
  return book.copies.some(c => c.status === 'available')
}

const handleQuickReserve = async (book) => {
  if (!authStore.isAuthenticated) {
    toast.add({ severity: 'warn', summary: 'Требуется вход', detail: 'Войдите в систему, чтобы забронировать книгу', life: 3000 })
    router.push(`/login?redirect=${route.fullPath}`)
    return
  }

  if (!isReader.value) {
    toast.add({ severity: 'warn', summary: 'Недоступно', detail: 'Бронирование доступно только для читателей', life: 3000 })
    return
  }

  reservingBook.value = book.id
  try {
    const result = await store.reserveBook({ bookId: book.id })
    if (result.success) {
      toast.add({
        severity: 'success',
        summary: 'Успешно',
        detail: result.message || `Книга "${book.title}" забронирована`,
        life: 4000
      })
      // После успешного бронирования обновляем данные
      await refreshCatalog()
    }
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.message || 'Не удалось оформить бронь'
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: errorMsg,
      life: 5000
    })
  } finally {
    reservingBook.value = null
  }
}

const applyFilters = async () => {
  await store.applyFilters()
  if (store.error) toast.add({ severity: 'error', summary: 'Ошибка', detail: store.error, life: 4000 })
}

const resetFilters = async () => {
  await store.resetFilters()
  if (store.error) toast.add({ severity: 'error', summary: 'Ошибка', detail: store.error, life: 4000 })
  else toast.add({ severity: 'info', summary: 'Сброшено', detail: 'Фильтры очищены', life: 2000 })
}

const onPageChange = (event) => { store.setPage(event.page + 1) }

const refreshCatalog = async () => {
  await store.loadBooks()
  if (store.error) toast.add({ severity: 'error', summary: 'Ошибка', detail: store.error, life: 4000 })
}

const getBookStatusText = (book) => {
  if (!book?.copies?.length) return 'Неизвестно'
  const available = book.copies.filter(c => c.status === 'available').length
  if (available === book.copies.length) return 'В наличии'
  if (available === 0) return 'Нет в наличии'
  return `Мало (${available}/${book.copies.length})`
}

const getBookStatusSeverity = (book) => {
  if (!book?.copies?.length) return 'secondary'
  const available = book.copies.filter(c => c.status === 'available').length
  if (available === book.copies.length) return 'success'
  if (available === 0) return 'danger'
  return 'warning'
}
</script>

<style scoped>
/* Обёртка с отступами */
.catalog-wrapper {
  padding: 0 32px 48px !important;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* Filter Bar */
.filter-bar {
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
}
.filter-item {
  flex: 1;
  min-width: 160px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.filter-actions-group {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  min-width: 240px;
  justify-content: flex-end;
}
.results-count {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}
.results-count strong { color: var(--primary); }

/* Cover Thumbnail */
.cover-thumb {
  width: 50px;
  height: 75px;
  border-radius: 6px;
  overflow: hidden;
  background: var(--surface-2);
  border: 1px solid var(--glass-border);
}
.cover-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* Book Title Link */
.book-title-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s;
}
.book-title-link:hover {
  opacity: 0.8;
  text-decoration: underline;
}

/* Table Overrides */
:deep(.p-datatable) { background: transparent !important; }
:deep(.p-datatable-thead > tr > th) {
  background: rgba(255,255,255,0.05) !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  font-size: 12px !important;
}
:deep(.p-datatable-tbody > tr:hover) {
  background: rgba(255,255,255,0.08) !important;
}

/* === Responsive (ИСПРАВЛЕНО) === */
@media (max-width: 768px) {
  .catalog-wrapper {
    padding: 0 16px 32px !important;
  }
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-actions-group {
    justify-content: space-between;
    min-width: auto;
  }
  .filter-item {
    min-width: 100%;
  }
}
</style>