<template>
  <div class="animate-fade-in">
    <!-- Заголовок с кнопкой обновления -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="dashboard-title">
          <i class="pi pi-chart-bar" style="color: var(--secondary);"></i>
          Обзор библиотеки
        </h1>
        <p class="dashboard-subtitle">Статистика фонда и текущих выдач</p>
      </div>
      <Button 
        icon="pi pi-refresh" 
        class="p-button-outlined p-button-sm"
        :loading="store.loading"
        @click="refreshData"
        title="Обновить данные"
      />
    </div>

    <!-- Loading State -->
    <div v-if="store.loading && !store.books.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка данных...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ store.error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="refreshData" />
    </div>

    <template v-else>
      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="glass stat-card accent-blue">
          <div class="stat-info">
            <h3>Всего книг</h3>
            <p>{{ store.totalBooks }}</p>
          </div>
          <i class="pi pi-book stat-icon" style="color: #3b82f6;"></i>
        </div>

        <div class="glass stat-card accent-cyan">
          <div class="stat-info">
            <h3>Активных займов</h3>
            <p>{{ activeLoans.length }}</p>
          </div>
          <i class="pi pi-sync stat-icon" style="color: #06b6d4;"></i>
        </div>

        <div class="glass stat-card accent-red">
          <div class="stat-info">
            <h3>Просрочено</h3>
            <p>{{ overdueCount }}</p>
          </div>
          <i class="pi pi-exclamation-triangle stat-icon" style="color: #ef4444;"></i>
        </div>

        <div class="glass stat-card accent-green">
          <div class="stat-info">
            <h3>В наличии</h3>
            <p>{{ store.availableCopies }}</p>
          </div>
          <i class="pi pi-check-circle stat-icon" style="color: #10b981;"></i>
        </div>
      </div>

      <!-- Secondary Grid -->
      <div class="dashboard-secondary-grid">
        <!-- Требуют внимания -->
        <div class="glass dashboard-card">
          <h3 class="card-title">
            <i class="pi pi-exclamation-triangle" style="color: var(--warning);"></i>
            Требуют внимания
          </h3>
          <div class="card-body">
            <ul class="attention-list">
              <li v-if="overdueCount > 0" class="attention-item">
                <span class="icon text-red-500"><i class="pi pi-times-circle"></i></span>
                <span class="text">{{ overdueCount }} просроченных займов</span>
              </li>
              <li v-if="expiringCount > 0" class="attention-item">
                <span class="icon text-orange-500"><i class="pi pi-clock"></i></span>
                <span class="text">{{ expiringCount }} заканчиваются (≤ 3 дней)</span>
              </li>
              <li class="attention-item">
                <span class="icon text-blue-500"><i class="pi pi-book"></i></span>
                <span class="text">{{ activeLoans.length }} книг на руках</span>
              </li>
              <li v-if="overdueCount === 0 && expiringCount === 0" class="attention-item">
                <span class="icon text-green-500"><i class="pi pi-check-circle"></i></span>
                <span class="text">Все в порядке</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Последние операции (динамическая секция) -->
        <div class="glass dashboard-card">
          <h3 class="card-title">
            <i class="pi pi-history" style="color: var(--text-secondary);"></i>
            Последние операции
          </h3>
          <div class="card-body">
            <div v-if="recentActivities.length" class="activity-list">
              <div v-for="act in recentActivities" :key="act.id" class="activity-item">
                <span class="activity-icon" :class="getActivityIconClass(act.type)">
                  <i :class="getActivityIcon(act.type)"></i>
                </span>
                <div class="activity-info">
                  <span class="activity-text">{{ act.description }}</span>
                  <span class="activity-time">{{ formatDate(act.timestamp) }}</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-state text-center py-4">
              <i class="pi pi-inbox text-3xl mb-2" style="color: var(--text-secondary); opacity: 0.4;"></i>
              <p class="text-secondary text-sm">Операций пока нет</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useInventoryStore } from '../../stores/inventoryStore'
import { formatDate } from '../../utils/formatters'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'

const store = useInventoryStore()

// Текущая дата для вычислений
const today = new Date()
today.setHours(0, 0, 0, 0)

// Загрузка данных при монтировании
onMounted(() => {
  refreshData()
})

// Ручное обновление
const refreshData = async () => {
  await store.init()
}

// Вычисляемые данные
const activeLoans = computed(() => store.activeLoans || [])

const overdueCount = computed(() => {
  return activeLoans.value.filter(loan => {
    if (!loan?.dueDate) return false
    const dueDate = new Date(loan.dueDate)
    return dueDate < today
  }).length
})

const expiringCount = computed(() => {
  return activeLoans.value.filter(loan => {
    if (!loan?.dueDate) return false
    const dueDate = new Date(loan.dueDate)
    const diffTime = dueDate - today
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays >= 0 && diffDays <= 3
  }).length
})

// Моковые данные для "Последние операции" (в реальности — из API)
const recentActivities = computed(() => {
  // В реальности: store.recentActivities или отдельный API-запрос
  // Здесь имитируем на основе последних действий в сторе
  return [
    {
      id: 1,
      type: 'checkout',
      description: 'Выдана книга "Война и мир" (Иван Петров)',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() // 2 часа назад
    },
    {
      id: 2,
      type: 'return',
      description: 'Возвращена книга "1984" (Анна Смирнова)',
      timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString() // 5 часов назад
    },
    {
      id: 3,
      type: 'reservation',
      description: 'Забронирована "Мастер и Маргарита" (Мария Козлова)',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() // вчера
    }
  ].slice(0, 5) // Показываем последние 5
})

// Утилиты для иконок активностей
const getActivityIcon = (type) => {
  const icons = {
    checkout: 'pi pi-upload',
    return: 'pi pi-download',
    reservation: 'pi pi-clock',
    add: 'pi pi-plus'
  }
  return icons[type] || 'pi pi-info-circle'
}

const getActivityIconClass = (type) => {
  const classes = {
    checkout: 'accent-blue',
    return: 'accent-green',
    reservation: 'accent-yellow',
    add: 'accent-cyan'
  }
  return classes[type] || 'accent-gray'
}
</script>

<style scoped>
/* Activity List Styles */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  transition: background 0.2s;
}
.activity-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 16px;
}
.activity-icon.accent-blue { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.activity-icon.accent-green { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.activity-icon.accent-yellow { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.activity-icon.accent-cyan { background: rgba(6, 182, 212, 0.15); color: #06b6d4; }
.activity-icon.accent-gray { background: rgba(156, 163, 175, 0.15); color: #9ca3af; }

.activity-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.activity-text {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.4;
}
.activity-time {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Attention List */
.attention-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.attention-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: var(--text-secondary);
}
.attention-item .icon {
  font-size: 16px;
  flex-shrink: 0;
}
.attention-item .text {
  line-height: 1.4;
}

/* Empty State */
.empty-state {
  padding: 24px 16px;
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 900px) {
  .dashboard-secondary-grid { grid-template-columns: 1fr; }
}
</style>