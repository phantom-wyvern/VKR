<template>
  <div class="animate-fade-in loans-wrapper">
    <div class="page-header mb-6">
      <div>
        <h1 class="page-title">
          <i class="pi pi-book"></i>
          Активные займы
        </h1>
        <p class="page-subtitle">Книги на руках у читателей и сроки возврата</p>
      </div>
      <Button
        icon="pi pi-refresh"
        class="p-button-outlined p-button-sm"
        :loading="loading"
        @click="loadLoans"
        title="Обновить данные"
      />
    </div>

    <!-- Статистика -->
    <div class="stats-grid mb-6">
      <div class="glass stat-card accent-blue">
        <div class="stat-info">
          <h3>Всего выдано</h3>
          <p>{{ activeLoans.length }}</p>
        </div>
        <i class="pi pi-book stat-icon" style="color: #3b82f6;"></i>
      </div>
      <div class="glass stat-card accent-red">
        <div class="stat-info">
          <h3>Просрочено</h3>
          <p>{{ overdueCount }}</p>
        </div>
        <i class="pi pi-exclamation-triangle stat-icon" style="color: #ef4444;"></i>
      </div>
      <div class="glass stat-card accent-yellow">
        <div class="stat-info">
          <h3>Заканчиваются (3 дня)</h3>
          <p>{{ expiringSoonCount }}</p>
        </div>
        <i class="pi pi-clock stat-icon" style="color: #f59e0b;"></i>
      </div>
      <div class="glass stat-card accent-green">
        <div class="stat-info">
          <h3>В срок</h3>
          <p>{{ onTimeCount }}</p>
        </div>
        <i class="pi pi-check-circle stat-icon" style="color: #10b981;"></i>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="filter-bar glass mb-6">
      <div class="filter-item">
        <label class="filter-label">Поиск</label>
        <InputText v-model="filters.search" placeholder="Читатель или книга" class="w-full" />
      </div>
      <div class="filter-item">
        <label class="filter-label">Статус</label>
        <Dropdown v-model="filters.status" :options="statusOptions" optionLabel="label" optionValue="value" placeholder="Все статусы" class="w-full" />
      </div>
      <div class="filter-actions-group">
        <Button label="Сбросить" icon="pi pi-undo" class="p-button-outlined p-button-sm" @click="resetFilters" />
      </div>
    </div>

    <!-- Загрузка -->
    <div v-if="loading && !loans.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка займов...</p>
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="loadLoans" />
    </div>

    <!-- Таблица -->
    <template v-else>
      <div class="table-container">
        <DataTable
          :value="filteredLoans"
          :loading="loading"
          stripedRows
          responsiveLayout="scroll"
          paginator
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20]"
          class="border-none"
          emptyMessage="Активных займов не найдено"
        >
          <Column field="readerName" header="Читатель" sortable>
            <template #body="{ data }">
              {{ data.readerName || '—' }}
            </template>
          </Column>
          <Column field="bookTitle" header="Книга" sortable>
            <template #body="{ data }">
              {{ data.bookTitle || '—' }}
            </template>
          </Column>
          <Column field="issueDate" header="Дата выдачи" sortable style="width: 120px">
            <template #body="{ data }">{{ formatDate(data.issueDate) }}</template>
          </Column>
          <Column field="dueDate" header="Вернуть до" sortable style="width: 120px">
            <template #body="{ data }">{{ formatDate(data.dueDate) }}</template>
          </Column>
          <Column header="Осталось дней" sortable style="width: 100px">
            <template #body="{ data }">
              <Tag
                :value="`${data.daysRemaining} ${getDaysLabel(data.daysRemaining)}`"
                :severity="data.daysRemaining < 0 ? 'danger' : data.daysRemaining <= 3 ? 'warning' : 'success'"
              />
            </template>
          </Column>
          <Column header="Статус" sortable style="width: 120px">
            <template #body="{ data }">
              <Tag
                :value="data.status === 'overdue' ? 'Просрочен' : data.status === 'expiring' ? 'Заканчивается' : 'В срок'"
                :severity="data.status === 'overdue' ? 'danger' : data.status === 'expiring' ? 'warning' : 'success'"
              />
            </template>
          </Column>
          <Column header="Действия" style="width: 120px">
            <template #body="{ data }">
              <Button
                label="Вернуть"
                icon="pi pi-check"
                class="p-button-sm p-button-success"
                :loading="returningId === data.id"
                @click="handleReturn(data)"
              />
            </template>
          </Column>
        </DataTable>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api/client'
import { useToast } from 'primevue/usetoast'
import { formatDate } from '../../utils/formatters'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'

const toast = useToast()

const activeLoans = ref([])
const loading = ref(false)
const error = ref(null)
const returningId = ref(null)

const filters = ref({
  search: '',
  status: 'all'
})

const statusOptions = [
  { label: 'Все', value: 'all' },
  { label: 'Просрочен', value: 'overdue' },
  { label: 'Заканчивается', value: 'expiring' },
  { label: 'В срок', value: 'active' }
]

const today = new Date()

const loans = computed(() => {
  return activeLoans.value.map(loan => {
    const due = new Date(loan.dueDate)
    const daysRemaining = Math.ceil((due - today) / (1000 * 60 * 60 * 24))
    let status = 'active'
    if (daysRemaining < 0) status = 'overdue'
    else if (daysRemaining <= 3) status = 'expiring'
    return { ...loan, daysRemaining, status }
  })
})

const overdueCount = computed(() => loans.value.filter(l => l.status === 'overdue').length)
const expiringSoonCount = computed(() => loans.value.filter(l => l.status === 'expiring').length)
const onTimeCount = computed(() => loans.value.filter(l => l.status === 'active').length)

const filteredLoans = computed(() => {
  let result = [...loans.value]

  if (filters.value.search) {
    const q = filters.value.search.toLowerCase()
    result = result.filter(l =>
      (l.readerName || '').toLowerCase().includes(q) ||
      (l.bookTitle || '').toLowerCase().includes(q)
    )
  }

  if (filters.value.status && filters.value.status !== 'all') {
    result = result.filter(l => l.status === filters.value.status)
  }

  return result
})

const getDaysLabel = (days) => {
  if (days < 0) return 'дн. назад'
  if (days === 0) return 'сегодня'
  if (days === 1) return 'день'
  if (days >= 2 && days <= 4) return 'дня'
  return 'дней'
}

const loadLoans = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/inventory/loans/active')
    activeLoans.value = response.data?.data || []
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Не удалось загрузить займы'
    console.error('Failed to load loans:', e)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = { search: '', status: 'all' }
}

const handleReturn = async (loan) => {
  if (!confirm(`Вернуть книгу "${loan.bookTitle}" от ${loan.readerName}?`)) return

  returningId.value = loan.id
  try {
    const response = await api.post('/inventory/return', { copyId: loan.copyId })
    if (response.data.success) {
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Книга возвращена', life: 3000 })
      await loadLoans()
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: e.response?.data?.detail || e.message, life: 4000 })
  } finally {
    returningId.value = null
  }
}

onMounted(() => loadLoans())
</script>

<style scoped>
.loans-wrapper {
  padding: 0 32px 48px !important;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info h3 {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin: 0 0 8px 0;
}

.stat-info p {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.stat-icon {
  font-size: 24px;
}

.filter-bar {
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
}

.filter-item {
  flex: 1;
  min-width: 200px;
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
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .loans-wrapper {
    padding: 0 16px 32px !important;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .filter-bar {
    flex-direction: column;
  }
}
</style>
