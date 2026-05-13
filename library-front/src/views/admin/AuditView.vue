<template>
  <div class="animate-fade-in audit-wrapper">
    <div class="page-header mb-6">
      <div>
        <h1 class="page-title">
          <i class="pi pi-history"></i>
          Журнал аудита
        </h1>
        <p class="page-subtitle">История всех действий в системе</p>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar glass mb-8">
      <div class="filter-group">
        <InputText 
          v-model="filters.search" 
          placeholder="Поиск по действию или пользователю" 
          class="w-full"
          @keyup.enter="applyFilters"
        />
      </div>
      
      <div class="filter-group">
        <Calendar 
          v-model="filters.dateRange" 
          selectionMode="range" 
          placeholder="Выберите период" 
          class="w-full"
          :manualInput="false"
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
          :loading="store.auditLoading"
          @click="applyFilters" 
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="store.auditLoading && !store.auditLogs.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка журнала...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ store.error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="loadLogs" />
    </div>

    <!-- Table -->
    <template v-else>
      <div class="table-container">
        <DataTable 
          :value="store.auditLogs" 
          stripedRows 
          responsiveLayout="scroll" 
          paginator 
          :rows="filters.limit"
          :totalRecords="store.auditTotal"
          :lazy="true"
          @page="onPageChange"
          class="border-none"
          emptyMessage="Записи не найдены"
        >
          <Column field="timestamp" header="Дата и время" sortable style="width: 180px">
            <template #body="{ data }">
              {{ formatDate(data.timestamp) }}
            </template>
          </Column>
          <Column field="userName" header="Пользователь" sortable></Column>
          <Column field="action" header="Действие" sortable></Column>
          <Column field="details" header="Детали">
            <template #body="{ data }">
              <span class="text-secondary">{{ data.details }}</span>
            </template>
          </Column>
        </DataTable>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../../stores/adminStore'
import { formatDate } from '../../utils/formatters'
import InputText from 'primevue/inputtext'
import Calendar from 'primevue/calendar'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ProgressSpinner from 'primevue/progressspinner'

const store = useAdminStore()

// Фильтры
const filters = ref({
  search: '',
  dateRange: null,
  page: 1,
  limit: 20
})

// Загрузка при монтировании
onMounted(() => {
  loadLogs()
})

// Основная функция загрузки
const loadLogs = async () => {
  await store.loadAuditLogs({
    search: filters.value.search,
    startDate: filters.value.dateRange?.[0]?.toISOString(),
    endDate: filters.value.dateRange?.[1]?.toISOString(),
    page: filters.value.page,
    limit: filters.value.limit
  })
}

// Применение фильтров (сброс на 1 страницу)
const applyFilters = () => {
  filters.value.page = 1
  loadLogs()
}

// Сброс фильтров
const resetFilters = () => {
  filters.value = {
    search: '',
    dateRange: null,
    page: 1,
    limit: 20
  }
  loadLogs()
}

// Обработка смены страницы (серверная пагинация)
const onPageChange = (event) => {
  filters.value.page = event.page + 1 // PrimeVue использует 0-based индекс
  filters.value.limit = event.rows
  loadLogs()
}
</script>

<style scoped>
/* Обёртка с отступами, как в Каталоге */
.audit-wrapper {
  padding: 0 32px 48px !important;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* Filter Bar Spacing */
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
  .audit-wrapper {
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