<template>
  <div class="animate-fade-in">
    <!-- Header with Refresh -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="page-title">
          <i class="pi pi-book" style="color: var(--primary);"></i>
          Мои займы
        </h1>
        <p class="page-subtitle">Управление вашими текущими займами книг</p>
      </div>
      <Button 
        icon="pi pi-refresh" 
        class="p-button-outlined p-button-sm"
        :loading="store.loading"
        @click="store.loadActiveLoans()"
        title="Обновить данные"
      />
    </div>

    <!-- Loading / Error States -->
    <div v-if="store.loading && !store.activeLoans.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка ваших книг...</p>
    </div>
    
    <div v-else-if="store.error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ store.error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="store.loadActiveLoans()" />
    </div>

    <template v-else>
      <!-- Table -->
      <div class="table-container">
        <DataTable 
          :value="loansWithDays" 
          stripedRows 
          class="border-none"
          emptyMessage="У вас нет активных займов. Найдите что-то почитать!"
        >
          <Column field="bookTitle" header="Книга" sortable></Column>
          <Column field="author" header="Автор" sortable></Column>
          
          <Column field="borrowDate" header="Дата выдачи" sortable style="width: 130px">
            <template #body="{ data }">{{ formatDate(data.borrowDate) }}</template>
          </Column>
          
          <Column field="dueDate" header="Вернуть до" sortable style="width: 130px">
            <template #body="{ data }">{{ formatDate(data.dueDate) }}</template>
          </Column>

          <Column header="Осталось" sortable style="width: 130px">
            <template #body="{ data }">
              <span :class="['days-badge', getDaysClass(data.daysRemaining)]">
                {{ data.daysLabel }}
              </span>
            </template>
          </Column>

          <Column header="Действия" style="width: 120px">
            <template #body="{ data }">
              <Button 
                v-if="data.daysRemaining > 0"
                label="Продлить" 
                icon="pi pi-refresh" 
                class="p-button-sm p-button-text p-button-secondary" 
                @click="openRenewDialog(data)" 
              />
              <span v-else class="text-error text-sm font-semibold">Просрочено</span>
            </template>
          </Column>
        </DataTable>
      </div>
    </template>

    <!-- Renew Dialog -->
    <Dialog v-model:visible="showRenewDialog" modal header="Продление срока" :style="{ width: '450px' }">
      <div class="flex flex-col gap-4">
        <p class="text-secondary">
          Вы уверены, что хотите продлить срок возврата книги <strong>"{{ selectedLoan?.bookTitle }}"</strong>?
        </p>
        <div class="p-3 bg-surface-1 rounded-lg border border-surface-2">
          <p class="text-sm mb-1">Новая дата возврата:</p>
          <p class="text-lg font-semibold text-primary">{{ newDueDate }}</p>
        </div>
      </div>
      <template #footer>
        <Button label="Отмена" icon="pi pi-times" class="p-button-text" @click="showRenewDialog = false" />
        <Button label="Подтвердить" icon="pi pi-check" class="p-button-primary" :loading="renewing" @click="confirmRenew" />
      </template>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLoanStore } from '../../stores/loanStore'
import { useToast } from 'primevue/usetoast'
import { formatDate } from '../../utils/formatters'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'

const store = useLoanStore()
const toast = useToast()

// Локальные состояния для диалога продления
const showRenewDialog = ref(false)
const selectedLoan = ref(null)
const renewing = ref(false)
const newDueDate = ref('')

// Вычисляемое свойство: обогащаем данные о займах информацией о днях
const loansWithDays = computed(() => {
  return store.activeLoans.map(loan => {
    const today = new Date()
    today.setHours(0,0,0,0)
    const due = new Date(loan.dueDate)
    const diffTime = due - today
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    let daysLabel = ''
    if (diffDays < 0) {
      daysLabel = `${Math.abs(diffDays)} дн. просрочки`
    } else if (diffDays === 0) {
      daysLabel = 'Сегодня'
    } else {
      daysLabel = `${diffDays} дн.`
    }
    
    return { ...loan, daysRemaining: diffDays, daysLabel }
  })
})

// Стили для бейджа дней
const getDaysClass = (days) => {
  if (days < 0) return 'overdue'
  if (days <= 3) return 'warning'
  return 'normal'
}

// Инициализация
onMounted(() => {
  if (!store.activeLoans.length) {
    store.loadActiveLoans()
  }
})

// Открытие диалога продления
const openRenewDialog = (loan) => {
  selectedLoan.value = loan
  
  // Имитация расчета новой даты (сейчас + 14 дней)
  const newDate = new Date(loan.dueDate)
  newDate.setDate(newDate.getDate() + 14)
  newDueDate.value = newDate.toLocaleDateString('ru-RU')
  
  showRenewDialog.value = true
}

// Подтверждение продления
const confirmRenew = async () => {
  renewing.value = true
  try {
    // Вызов стора
    const result = await store.renewLoan(selectedLoan.value.id)
    
    if (result.success) {
      toast.add({ severity: 'success', summary: 'Успешно', detail: `Срок продлён до ${newDueDate.value}`, life: 3000 })
      showRenewDialog.value = false
      store.loadActiveLoans() // Обновить список
    } else {
      throw new Error(result.error || 'Не удалось продлить')
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: e.message, life: 4000 })
  } finally {
    renewing.value = false
  }
}
</script>

<style scoped>
.days-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
  text-align: center;
  min-width: 80px;
}
.days-badge.normal {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}
.days-badge.warning {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}
.days-badge.overdue {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}
</style>