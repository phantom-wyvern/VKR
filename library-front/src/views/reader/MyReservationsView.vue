<template>
  <div class="animate-fade-in">
    <!-- Header with Refresh -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="page-title">
          <i class="pi pi-calendar" style="color: var(--primary);"></i>
          Мои бронирования
        </h1>
        <p class="page-subtitle">Статус ваших текущих бронирований книг</p>
      </div>
      <Button 
        icon="pi pi-refresh" 
        class="p-button-outlined p-button-sm"
        :loading="store.loading"
        @click="store.loadReservations()"
        title="Обновить данные"
      />
    </div>

    <!-- Loading / Error States -->
    <div v-if="store.loading && !store.reservations.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка бронирований...</p>
    </div>
    
    <div v-else-if="store.error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ store.error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="store.loadReservations()" />
    </div>

    <template v-else>
      <!-- Table -->
      <div class="table-container">
        <DataTable 
          :value="store.reservations" 
          stripedRows 
          class="border-none"
          emptyMessage="У вас нет активных бронирований"
        >
          <Column field="bookTitle" header="Книга" sortable>
            <template #body="{ data }">
              <router-link :to="getBookRoute(data.bookId)" class="book-title-link">
                {{ data.bookTitle }}
              </router-link>
            </template>
          </Column>
          <Column field="author" header="Автор" sortable></Column>
          
          <Column field="createdAt" header="Дата бронирования" sortable style="width: 140px">
            <template #body="{ data }">{{ formatDate(data.createdAt) }}</template>
          </Column>
          
          <Column header="Статус" sortable>
            <template #body="{ data }">
              <Tag :value="getStatusText(data.status)" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column header="Действия" style="width: 140px">
            <template #body="{ data }">
              <Button 
                v-if="['pending', 'ready'].includes(data.status)"
                label="Отменить" 
                icon="pi pi-times" 
                class="p-button-sm p-button-text p-button-danger" 
                @click="openCancelDialog(data)" 
              />
              <span v-else class="text-secondary text-sm">—</span>
            </template>
          </Column>
        </DataTable>
      </div>
    </template>

    <!-- Cancel Confirmation Dialog -->
    <Dialog v-model:visible="showCancelDialog" modal header="Отмена бронирования" :style="{ width: '450px' }">
      <div class="flex flex-col gap-3">
        <p class="text-secondary">
          Вы уверены, что хотите отменить бронирование книги <strong>"{{ selectedReservation?.bookTitle }}"</strong>?
        </p>
        <p class="text-sm text-secondary">Это действие нельзя отменить, а книга вернётся в общий доступ.</p>
      </div>
      <template #footer>
        <Button label="Нет" icon="pi pi-times" class="p-button-text" @click="showCancelDialog = false" />
        <Button label="Да, отменить" icon="pi pi-check" class="p-button-danger" :loading="cancelling" @click="confirmCancel" />
      </template>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLoanStore } from '../../stores/loanStore'
import { useToast } from 'primevue/usetoast'
import { formatDate } from '../../utils/formatters'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'

const router = useRouter()
const store = useLoanStore()
const toast = useToast()

const showCancelDialog = ref(false)
const selectedReservation = ref(null)
const cancelling = ref(false)

// Загрузка при монтировании
onMounted(() => {
  if (!store.reservations.length) {
    store.loadReservations()
  }
})

// Навигация к книге
const getBookRoute = (bookId) => {
  return { name: 'reader-book-detail', params: { id: bookId } }
}

// Утилиты статусов
const getStatusText = (status) => {
  const map = {
    pending: 'В очереди',
    ready: 'Готово к выдаче',
    fulfilled: 'Выдана',
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

// Открытие диалога отмены
const openCancelDialog = (reservation) => {
  selectedReservation.value = reservation
  showCancelDialog.value = true
}

// Подтверждение отмены
const confirmCancel = async () => {
  cancelling.value = true
  try {
    const result = await store.cancelReservation(selectedReservation.value.id)
    
    if (result.success) {
      toast.add({ 
        severity: 'success', 
        summary: 'Успешно', 
        detail: 'Бронирование отменено', 
        life: 3000 
      })
      showCancelDialog.value = false
      selectedReservation.value = null
      store.loadReservations() // Обновить список
    } else {
      throw new Error(result.error || 'Не удалось отменить бронирование')
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
</script>

<style scoped>
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
</style>