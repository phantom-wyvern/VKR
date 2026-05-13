<template>
  <div class="animate-fade-in fines-wrapper">
    <div class="page-header mb-6">
      <div>
        <h1 class="page-title">
          <i class="pi pi-money-bill" style="color: var(--danger);"></i>
          Штрафы и задолженности
        </h1>
        <p class="page-subtitle">Просроченные книги и начисленные штрафы</p>
      </div>
      <Button
        icon="pi pi-refresh"
        class="p-button-outlined p-button-sm"
        :loading="store.loading"
        @click="loadFines"
        title="Обновить данные"
      />
    </div>

    <!-- Stats -->
    <div class="stats-grid mb-6">
      <div class="glass stat-card accent-red">
        <div class="stat-info">
          <h3>Всего штрафов</h3>
          <p>{{ fines.length }}</p>
        </div>
        <i class="pi pi-exclamation-triangle stat-icon" style="color: #ef4444;"></i>
      </div>
      <div class="glass stat-card accent-blue">
        <div class="stat-info">
          <h3>Общая сумма</h3>
          <p>{{ totalAmount }} ₽</p>
        </div>
        <i class="pi pi-wallet stat-icon" style="color: #3b82f6;"></i>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading && !fines.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка штрафов...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="loadFines" />
    </div>

    <!-- Table -->
    <template v-else>
      <div class="table-container">
        <DataTable
          :value="fines"
          :loading="store.loading"
          stripedRows
          responsiveLayout="scroll"
          paginator
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20]"
          class="border-none"
          emptyMessage="Нет штрафов"
        >
          <Column field="userName" header="Читатель" sortable></Column>
          <Column field="reason" header="Причина" sortable></Column>
          <Column field="date" header="Дата" sortable style="width: 130px">
            <template #body="{ data }">{{ formatDate(data.date) }}</template>
          </Column>
          <Column field="amount" header="Сумма" sortable style="width: 100px">
            <template #body="{ data }">
              <span class="font-semibold text-danger">{{ data.amount }} ₽</span>
            </template>
          </Column>
          <Column header="Статус" style="width: 120px">
            <template #body="{ data }">
              <Tag :value="data.paid ? 'Оплачен' : 'Не оплачен'" :severity="data.paid ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column header="Действия" style="width: 130px">
            <template #body="{ data }">
              <Button
                v-if="!data.paid"
                label="Оплатить"
                icon="pi pi-check"
                class="p-button-sm p-button-outlined p-button-success"
                :loading="payingId === data.id"
                @click="handlePay(data)"
              />
              <span v-else class="text-secondary text-sm">—</span>
            </template>
          </Column>
        </DataTable>
      </div>
    </template>
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
import ProgressSpinner from 'primevue/progressspinner'
import api from '../../api/client'

const store = useInventoryStore()
const toast = useToast()

const fines = ref([])
const error = ref(null)
const payingId = ref(null)

const totalAmount = computed(() => fines.value.reduce((sum, f) => sum + (f.amount || 0), 0))

const loadFines = async () => {
  store.loading = true
  error.value = null
  try {
    const response = await api.get('/inventory/fines')
    fines.value = response.data || []
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Не удалось загрузить штрафы'
  } finally {
    store.loading = false
  }
}

const handlePay = async (fine) => {
  payingId.value = fine.id
  try {
    await api.patch(`/inventory/fines/${fine.id}/pay`)
    fine.paid = true
    toast.add({ severity: 'success', summary: 'Успешно', detail: 'Штраф отмечен как оплаченный', life: 3000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: e.response?.data?.detail || e.message, life: 4000 })
  } finally {
    payingId.value = null
  }
}

onMounted(() => loadFines())
</script>

<style scoped>
.fines-wrapper {
  padding: 0 32px 48px !important;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
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

.stat-icon { font-size: 24px; }

@media (max-width: 600px) {
  .fines-wrapper { padding: 0 16px 32px !important; }
  .stats-grid { grid-template-columns: 1fr; }
}
</style>
