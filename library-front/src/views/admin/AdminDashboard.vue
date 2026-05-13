<template>
  <div class="animate-fade-in">
    <!-- Заголовок с кнопкой обновления -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="dashboard-title">
          <i class="pi pi-chart-line" style="color: var(--primary);"></i>
          Обзор системы
        </h1>
        <p class="dashboard-subtitle">Ключевые показатели и статистика библиотеки</p>
      </div>
      <Button 
        icon="pi pi-refresh" 
        class="p-button-outlined p-button-sm"
        :loading="store.loading"
        @click="refreshData"
        title="Обновить данные"
      />
    </div>

    <!-- Состояние загрузки -->
    <div v-if="store.loading && !store.users.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка статистики...</p>
    </div>

    <!-- Состояние ошибки -->
    <div v-else-if="store.error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ store.error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="refreshData" />
    </div>

    <template v-else>
      <!-- Top Stats Grid -->
      <div class="stats-grid">
        <div class="glass stat-card accent-blue">
          <div class="stat-info">
            <h3>Всего пользователей</h3>
            <p>{{ store.totalUsers }}</p>
          </div>
          <i class="pi pi-users stat-icon" style="color: #3b82f6;"></i>
        </div>
        <div class="glass stat-card accent-green">
          <div class="stat-info">
            <h3>Активных</h3>
            <p>{{ store.activeUsers }}</p>
          </div>
          <i class="pi pi-check-circle stat-icon" style="color: #10b981;"></i>
        </div>
        <div class="glass stat-card accent-red">
          <div class="stat-info">
            <h3>Заблокировано</h3>
            <p>{{ store.blockedUsers }}</p>
          </div>
          <i class="pi pi-ban stat-icon" style="color: #ef4444;"></i>
        </div>
        <div class="glass stat-card accent-yellow">
          <div class="stat-info">
            <h3>Жанров</h3>
            <p>{{ store.genres.length }}</p>
          </div>
          <i class="pi pi-tags stat-icon" style="color: #f59e0b;"></i>
        </div>
      </div>

      <!-- Bottom Section -->
      <div class="dashboard-secondary-grid">
        <!-- Roles Card -->
        <div class="glass dashboard-card">
          <h3 class="card-title">
            <i class="pi pi-chart-pie" style="color: var(--secondary);"></i>
            Пользователи по ролям
          </h3>
          <div class="card-list">
            <div v-for="(count, role) in store.usersByRole" :key="role" class="list-row">
              <span class="row-label">{{ getRoleName(role) }}</span>
              <Tag :value="count" severity="info" />
            </div>
          </div>
        </div>

        <!-- Settings Card -->
        <div class="glass dashboard-card">
          <h3 class="card-title">
            <i class="pi pi-sliders-h" style="color: var(--warning);"></i>
            Параметры системы
          </h3>
          <div class="card-list">
            <div class="list-row">
              <span class="row-label">Срок выдачи (дней)</span>
              <span class="row-value">{{ store.settings?.loanPeriod ?? '—' }}</span>
            </div>
            <div class="list-row">
              <span class="row-label">Макс. книг на руки</span>
              <span class="row-value">{{ store.settings?.maxBooksPerUser ?? '—' }}</span>
            </div>
            <div class="list-row">
              <span class="row-label">Штраф за день</span>
              <span class="row-value">{{ store.settings?.finePerDay ?? '—' }} ₽</span>
            </div>
            <div class="list-row">
              <span class="row-label">Бронирования</span>
              <Tag 
                :value="store.settings?.enableReservations ? 'Вкл' : 'Выкл'" 
                :severity="store.settings?.enableReservations ? 'success' : 'secondary'" 
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAdminStore } from '../../stores/adminStore'
import { getRoleName } from '../../utils/formatters'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'

const store = useAdminStore()

// Загрузка данных при монтировании компонента
onMounted(async () => {
  await store.init()
})

// Ручное обновление данных
const refreshData = async () => {
  await store.init()
}
</script>