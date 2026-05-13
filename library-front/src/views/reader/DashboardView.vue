<template>
  <div class="animate-fade-in">
    <!-- Заголовок с кнопкой обновления -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="dashboard-title">
          <i class="pi pi-user" style="color: var(--primary);"></i>
          Добро пожаловать, {{ auth.user?.name }}
        </h1>
        <p class="dashboard-subtitle">Управляйте своими займами и бронированиями</p>
      </div>
      <Button 
        icon="pi pi-refresh" 
        class="p-button-outlined p-button-sm"
        :loading="loanStore.loading"
        @click="refreshData"
        title="Обновить данные"
      />
    </div>

    <!-- Loading State -->
    <div v-if="loanStore.loading && !loanStore.activeLoans?.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка данных...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="loanStore.error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ loanStore.error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="refreshData" />
    </div>

    <template v-else>
      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="glass stat-card accent-blue">
          <div class="stat-info">
            <h3>Активные займы</h3>
            <p>{{ loanStats.activeCount }}</p>
          </div>
          <i class="pi pi-book stat-icon" style="color: #3b82f6;"></i>
        </div>
        
        <div class="glass stat-card accent-red">
          <div class="stat-info">
            <h3>Просрочено</h3>
            <p>{{ loanStats.overdueCount }}</p>
          </div>
          <i class="pi pi-exclamation-triangle stat-icon" style="color: #ef4444;"></i>
        </div>
        
        <div class="glass stat-card accent-green">
          <div class="stat-info">
            <h3>Готово к выдаче</h3>
            <p>{{ loanStats.readyReservations }}</p>
          </div>
          <i class="pi pi-check-circle stat-icon" style="color: #10b981;"></i>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-bar">
        <router-link to="/cabinet/catalog">
          <Button label="Каталог книг" icon="pi pi-book" class="p-button-outlined" />
        </router-link>
        <router-link to="/cabinet/loans">
          <Button label="Мои книги" icon="pi pi-list" class="p-button-primary" />
        </router-link>
        <router-link to="/cabinet/reservations">
          <Button
            label="Мои бронирования"
            icon="pi pi-calendar"
            class="p-button-outlined"
            :badge="loanStore.reservations.filter(r => r.status === 'ready').length || undefined"
          />
        </router-link>
      </div>

      <!-- Quick Info: Ближайший возврат -->
      <div v-if="loanStats.nextDueDate" class="glass mt-6 p-4 rounded-xl">
        <div class="flex items-center gap-3">
          <i class="pi pi-clock text-warning" style="font-size: 20px;"></i>
          <div>
            <span class="text-secondary text-sm">Ближайший возврат:</span>
            <p class="font-semibold text-primary">{{ formatDate(loanStats.nextDueDate) }}</p>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import { useLoanStore } from '../../stores/loanStore'
import { useToast } from 'primevue/usetoast'
import { formatDate } from '../../utils/formatters'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'

const auth = useAuthStore()
const loanStore = useLoanStore()
const toast = useToast()

// Вычисляемая статистика (централизованная логика)
const loanStats = computed(() => {
  const loans = loanStore.activeLoans || []
  const reservations = loanStore.reservations || []
  
  const activeCount = loans.length
  const overdueCount = loans.filter(loan => {
    if (!loan?.dueDate) return false
    return new Date(loan.dueDate) < new Date()
  }).length
  
  const readyReservations = reservations.filter(r => r.status === 'ready').length
  
  // Ближайшая дата возврата
  const nextDueDate = loans
    .filter(l => l.status === 'active' && l.dueDate)
    .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate))[0]?.dueDate || null
  
  return {
    activeCount,
    overdueCount,
    readyReservations,
    nextDueDate
  }
})

// Загрузка данных при монтировании
onMounted(async () => {
  await refreshData()
})

// Ручное обновление
const refreshData = async () => {
  try {
    // Загружаем параллельно займы и бронирования
    await Promise.all([
      loanStore.loadActiveLoans?.(),
      loanStore.loadReservations?.()
    ])
  } catch (e) {
    toast.add({ 
      severity: 'error', 
      summary: 'Ошибка', 
      detail: 'Не удалось обновить данные', 
      life: 4000 
    })
  }
}
</script>

<style scoped>
.action-bar {
  display: flex;
  gap: 16px;
  margin-top: 24px;
  flex-wrap: wrap;
}

/* Адаптивность */
@media (max-width: 640px) {
  .action-bar { flex-direction: column; }
  .action-bar .p-button { width: 100%; justify-content: center; }
}
</style>