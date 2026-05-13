<template>
  <div class="reservations-wrapper">
    <div class="page-header mb-6">
      <div>
        <h1 class="page-title">
          <i class="pi pi-clock"></i>
          Очередь бронирований
        </h1>
        <p class="page-subtitle">Управление очередью бронирований книг</p>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar glass mb-8">
      <div class="filter-group">
        <InputText 
          v-model="filters.search" 
          placeholder="Поиск по книге или читателю" 
          class="w-full" 
          @keyup.enter="applyFilters" 
        />
      </div>
      <div class="filter-group">
        <Dropdown 
          v-model="filters.status" 
          :options="statusOptions" 
          placeholder="Все статусы" 
          class="w-full" 
          showClear 
        />
      </div>
      <div class="filter-actions-group">
        <Button 
          label="Сбросить" 
          icon="pi pi-refresh" 
          class="p-button-outlined p-button-sm" 
          @click="resetFilters" 
        />
        <Button 
          label="Применить" 
          icon="pi pi-filter" 
          :loading="store.loading" 
          @click="applyFilters" 
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading && !store.reservations.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка бронирований...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ store.error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="loadReservations" />
    </div>

    <!-- Table -->
    <template v-else>
      <div class="table-container">
        <DataTable 
          :value="filteredReservations" 
          stripedRows 
          responsiveLayout="scroll" 
          paginator
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20]"
          class="border-none"
          emptyMessage="Бронирования не найдены"
        >
          <Column field="bookTitle" header="Книга" sortable></Column>
          <Column field="userName" header="Читатель" sortable></Column>
          <Column field="date" header="Дата бронирования" sortable style="width: 140px">
            <template #body="{ data }">{{ formatDate(data.date) }}</template>
          </Column>
          <Column field="queuePosition" header="Очередь" sortable style="width: 100px">
            <template #body="{ data }">
              <Tag v-if="data.queuePosition" :value="`#${data.queuePosition}`" severity="info" />
              <span v-else class="text-secondary">—</span>
            </template>
          </Column>
          <Column header="Статус" sortable style="width: 130px">
            <template #body="{ data }">
              <Tag :value="getStatusText(data.status)" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Действия" style="width: 180px">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button 
                  v-if="data.status === 'pending'" 
                  label="Подтвердить" 
                  icon="pi pi-check" 
                  class="p-button-sm p-button-success" 
                  :loading="approvingId === data.id"
                  @click="confirmApprove(data)" 
                />
                <Button 
                  v-if="data.status === 'ready'" 
                  label="Выдать" 
                  icon="pi pi-upload" 
                  class="p-button-sm p-button-primary" 
                  @click="fulfillReservation(data)"
                />
                <Button 
                  icon="pi pi-times" 
                  class="p-button-sm p-button-text p-button-danger" 
                  @click="confirmCancel(data)"
                  title="Отменить"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </template>

    <!-- Confirmation Dialogs -->
    <Dialog v-model:visible="showApproveDialog" modal header="Подтвердить бронирование" :style="{ width: '400px' }">
      <p class="mb-4">
        Подтвердить бронирование книги <strong>"{{ selectedReservation?.bookTitle }}"</strong> для <strong>{{ selectedReservation?.userName }}</strong>?
      </p>
      <template #footer>
        <Button label="Отмена" icon="pi pi-times" class="p-button-text" @click="showApproveDialog = false" />
        <Button label="Подтвердить" icon="pi pi-check" class="p-button-success" :loading="approving" @click="approveReservation" />
      </template>
    </Dialog>

    <Dialog v-model:visible="showCancelDialog" modal header="Отменить бронирование" :style="{ width: '400px' }">
      <p class="mb-4">
        Отменить бронирование книги <strong>"{{ selectedReservation?.bookTitle }}"</strong>? Это действие нельзя отменить.
      </p>
      <template #footer>
        <Button label="Отмена" icon="pi pi-times" class="p-button-text" @click="showCancelDialog = false" />
        <Button label="Отменить" icon="pi pi-times" class="p-button-danger" :loading="cancelling" @click="cancelReservation" />
      </template>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useInventoryStore } from '../../stores/inventoryStore'
import { useToast } from 'primevue/usetoast'
import { formatDate } from '../../utils/formatters'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'

const store = useInventoryStore()
const toast = useToast()

// Фильтры
const filters = ref({
  search: '',
  status: null
})

const statusOptions = [
  { label: 'Все', value: 'all' },
  { label: 'Ожидает', value: 'pending' },
  { label: 'Готово к выдаче', value: 'ready' },
  { label: 'Выполнено', value: 'fulfilled' },
  { label: 'Отменено', value: 'cancelled' }
]

// Состояния диалогов и действий
const showApproveDialog = ref(false)
const showCancelDialog = ref(false)
const selectedReservation = ref(null)
const approving = ref(false)
const cancelling = ref(false)
const approvingId = ref(null)

// Загрузка при монтировании
onMounted(async () => {
  await Promise.all([
    store.loadReservations(),
    store.loadBooks()
  ])
})

const loadReservations = async () => {
  await store.loadReservations()
}

// Фильтрация (клиентская, для мока)
const filteredReservations = computed(() => {
  let result = [...(store.reservations || [])]
  
  if (filters.value.search) {
    const q = filters.value.search.toLowerCase()
    result = result.filter(r => 
      r.bookTitle?.toLowerCase().includes(q) || 
      r.userName?.toLowerCase().includes(q)
    )
  }
  
  if (filters.value.status) {
    result = result.filter(r => r.status === filters.value.status)
  }
  
  // Сортировка: сначала ожидающие, потом по дате
  result.sort((a, b) => {
    if (a.status === 'pending' && b.status !== 'pending') return -1
    if (a.status !== 'pending' && b.status === 'pending') return 1
    return new Date(b.date) - new Date(a.date)
  })
  
  return result
})

const applyFilters = () => {
  // Для клиентской фильтрации достаточно пересчёта computed
}

const resetFilters = () => {
  filters.value = { search: '', status: null }
}

// Утилиты статусов
const getStatusText = (status) => {
  const map = {
    pending: 'Ожидает',
    ready: 'Готово к выдаче',
    fulfilled: 'Выполнено',
    cancelled: 'Отменено'
  }
  return map[status] || status
}

const getStatusSeverity = (status) => {
  const map = {
    pending: 'warning',
    ready: 'success',
    fulfilled: 'info',
    cancelled: 'secondary'
  }
  return map[status] || 'secondary'
}

// Подтверждение бронирования (с диалогом)
const confirmApprove = (reservation) => {
  selectedReservation.value = reservation
  showApproveDialog.value = true
}

const approveReservation = async () => {
  if (!selectedReservation.value) return
  
  approving.value = true
  try {
    const result = await store.approveReservation(selectedReservation.value.id)
    
    if (result.success) {
      toast.add({ 
        severity: 'success', 
        summary: 'Успешно', 
        detail: `Бронирование "${selectedReservation.value.bookTitle}" подтверждено`, 
        life: 3000 
      })
      showApproveDialog.value = false
      selectedReservation.value = null
      await loadReservations()
    } else {
      throw new Error(result.error || 'Ошибка подтверждения')
    }
  } catch (e) {
    toast.add({ 
      severity: 'error', 
      summary: 'Ошибка', 
      detail: e.message, 
      life: 4000 
    })
  } finally {
    approving.value = false
  }
}

// Отмена бронирования (с диалогом)
const confirmCancel = (reservation) => {
  selectedReservation.value = reservation
  showCancelDialog.value = true
}

const cancelReservation = async () => {
  if (!selectedReservation.value) return
  
  cancelling.value = true
  try {
    const result = await store.cancelReservation(selectedReservation.value.id)
    
    if (result.success) {
      toast.add({ 
        severity: 'info', 
        summary: 'Отменено', 
        detail: `Бронирование "${selectedReservation.value.bookTitle}" отменено`, 
        life: 3000 
      })
      showCancelDialog.value = false
      selectedReservation.value = null
      await loadReservations()
    } else {
      throw new Error(result.error || 'Ошибка отмены')
    }
  } catch (e) {
    toast.add({ 
      severity: 'error', 
      summary: 'Ошибка', 
      detail: e.message, 
      life: 4000 
    })
  } finally {
    cancelling.value = false
  }
}

// Выдача книги по подтверждённому бронированию
const fulfillReservation = async (reservation) => {
  // Находим первый доступный экземпляр книги
  const book = store.books.find(b => b.id === reservation.bookId)
  const availableCopy = book?.copies?.find(c => c.status === 'available')

  if (!availableCopy) {
    toast.add({
      severity: 'warn',
      summary: 'Недоступно',
      detail: `Нет свободных экземпляров книги "${reservation.bookTitle}"`,
      life: 4000
    })
    return
  }

  if (!confirm(`Выдать книгу "${reservation.bookTitle}" (экз. #${availableCopy.id}) читателю ${reservation.userName}?`)) return

  approvingId.value = reservation.id
  try {
    // Выдаём книгу + автоматически отмечаем бронирование как выполненное
    const result = await store.checkoutBook({
      copyId: availableCopy.id,
      userId: reservation.userId,
      userName: reservation.userName,
      reservationId: reservation.id
    })

    if (result.success) {
      toast.add({
        severity: 'success',
        summary: 'Выдано',
        detail: `Книга "${reservation.bookTitle}" выдана`,
        life: 3000
      })
      await loadReservations()
    } else {
      throw new Error(result.message)
    }
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: e.response?.data?.detail || e.message || 'Не удалось выдать книгу',
      life: 4000
    })
  } finally {
    approvingId.value = null
  }
}
</script>

<style scoped>
/* Обёртка с отступами, как в других страницах */
.reservations-wrapper {
  padding: 0 32px 48px !important;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* Filter Bar с правильными отступами */
.filter-bar {
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
}
.filter-group {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-actions-group {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  min-width: 240px;
  justify-content: flex-end;
}

/* Адаптивность */
@media (max-width: 768px) {
  .reservations-wrapper {
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
  .filter-group {
    min-width: 100%;
  }
}
</style>