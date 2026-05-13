<template>
  <div class="app-layout">
    <!-- Header -->
    <header class="glass layout-header">
      <router-link to="/librarian" class="logo-btn">
        <div class="icon-wrap">
          <i class="pi pi-desktop"></i>
        </div>
        <span>Панель библиотекаря</span>
      </router-link>

      <div class="user-header">
        <!-- Имя с индикацией загрузки -->
        <span v-if="loading" class="user-name text-secondary">Загрузка...</span>
        <span v-else class="user-name">{{ userName }}</span>
        
        <!-- Статистика (опционально, можно показать бейджи) -->
        <div v-if="stats && !loading" class="user-stats hidden-sm">
          <span v-if="stats.pendingReservations > 0" class="stat-badge warning" title="Бронирования">
            <i class="pi pi-clock"></i> {{ stats.pendingReservations }}
          </span>
          <span v-if="stats.overdueLoans > 0" class="stat-badge danger" title="Просрочено">
            <i class="pi pi-exclamation-triangle"></i> {{ stats.overdueLoans }}
          </span>
        </div>
        
        <Button 
          :label="loading ? '...' : 'Выйти'" 
          icon="pi pi-sign-out" 
          class="p-button-sm p-button-text" 
          :disabled="loading"
          @click="handleLogout" 
        />
      </div>
    </header>

    <!-- Main Body -->
    <div class="layout-body">
      <!-- Sidebar -->
      <aside class="layout-sidebar glass">
        <!-- Динамическое меню из композабла -->
        <template v-if="menuItems.length">
          <router-link 
            v-for="item in menuItems" 
            :key="item.id"
            :to="item.path" 
            class="nav-link" 
            active-class="router-link-active"
          >
            <i :class="item.icon"></i> {{ item.label }}
            <!-- Бейдж уведомлений для пунктов меню -->
            <span v-if="getMenuItemBadge(item.id)" class="nav-badge" :class="getMenuItemBadgeClass(item.id)">
              {{ getMenuItemBadge(item.id) }}
            </span>
          </router-link>
        </template>
        
        <!-- Фолбэк: статическое меню -->
        <template v-else>
          <router-link to="/librarian" class="nav-link" active-class="router-link-active">
            <i class="pi pi-home"></i> Главная
          </router-link>
          <router-link to="/librarian/checkout" class="nav-link" active-class="router-link-active">
            <i class="pi pi-sync"></i> Выдача / Возврат
          </router-link>
          <router-link to="/librarian/inventory" class="nav-link" active-class="router-link-active">
            <i class="pi pi-list"></i> Фонд
          </router-link>
          <router-link to="/librarian/reservations" class="nav-link" active-class="router-link-active">
            <i class="pi pi-clock"></i> Бронирования
          </router-link>
          <router-link to="/librarian/loans" class="nav-link" active-class="router-link-active">
            <i class="pi pi-book"></i> Займы
          </router-link>
          <router-link to="/librarian/fines" class="nav-link" active-class="router-link-active">
            <i class="pi pi-money-bill"></i> Штрафы
          </router-link>
          <router-link to="/librarian/reports" class="nav-link" active-class="router-link-active">
            <i class="pi pi-chart-line"></i> Отчёты
          </router-link>
        </template>
      </aside>

      <!-- Content -->
      <main class="layout-content animate-fade-in">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useLibrarianLayout } from '../composables/useLibrarianLayout'
import Button from 'primevue/button'

const { 
  userName, 
  userRole, 
  menuItems, 
  stats, 
  loading, 
  handleLogout, 
  checkPermission,
  refreshStats 
} = useLibrarianLayout()

// Вспомогательные функции для бейджей в меню
const getMenuItemBadge = (itemId) => {
  if (!stats.value) return null
  if (itemId === 'reservations' && stats.value.pendingReservations > 0) {
    return stats.value.pendingReservations
  }
  if (itemId === 'loans' && stats.value.overdueLoans > 0) {
    return stats.value.overdueLoans
  }
  return null
}

const getMenuItemBadgeClass = (itemId) => {
  if (itemId === 'reservations') return 'warning'
  if (itemId === 'loans') return 'danger'
  return 'info'
}
</script>

<style scoped>
.user-stats {
  display: flex;
  gap: 8px;
  margin-right: 12px;
}

.stat-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}
.stat-badge.warning {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}
.stat-badge.danger {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.nav-badge {
  margin-left: auto;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}
.nav-badge.warning {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}
.nav-badge.danger {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}
.nav-badge.info {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

@media (max-width: 1024px) {
  .hidden-sm { display: none; }
}
</style>