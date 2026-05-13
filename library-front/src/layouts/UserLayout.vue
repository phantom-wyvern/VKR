<template>
  <div class="app-layout">
    <!-- Header -->
    <header class="glass layout-header">
      <router-link to="/cabinet" class="logo-btn">
        <div class="icon-wrap">
          <i class="pi pi-user"></i>
        </div>
        <span>Личный кабинет</span>
      </router-link>
      
      <div class="user-header">
        <!-- Имя с индикацией загрузки -->
        <span v-if="loading" class="user-name text-secondary">Загрузка...</span>
        <span v-else class="user-name">{{ userName }}</span>
        
        <!-- Статистика (опционально, бейджи в хедере) -->
        <div v-if="stats && !loading" class="user-stats hidden-sm">
          <span v-if="stats.activeLoans > 0" class="stat-badge info" title="Активные займы">
            <i class="pi pi-book"></i> {{ stats.activeLoans }}
          </span>
          <span v-if="stats.unreadNotifications > 0" class="stat-badge warning" title="Уведомления">
            <i class="pi pi-bell"></i> {{ stats.unreadNotifications }}
          </span>
        </div>
        
        <Button 
          :label="loading ? '...' : 'Выйти'" 
          icon="pi pi-sign-out" 
          class="p-button-sm p-button-outlined" 
          :disabled="loading"
          @click="handleLogout" 
        />
      </div>
    </header>

    <!-- Main Body -->
    <div class="layout-body">
      <!-- Sidebar -->
      <aside class="layout-sidebar glass" style="padding: 16px;">
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
            <span v-if="getMenuItemBadge(item.id)" class="nav-badge info">
              {{ getMenuItemBadge(item.id) }}
            </span>
          </router-link>
        </template>
        
        <!-- Фолбэк: статическое меню -->
        <template v-else>
          <router-link to="/cabinet" class="nav-link" active-class="router-link-active">
            <i class="pi pi-home"></i> Главная
          </router-link>
          <router-link to="/cabinet/catalog" class="nav-link" active-class="router-link-active">
            <i class="pi pi-book"></i> Каталог
          </router-link>
          <router-link to="/cabinet/loans" class="nav-link" active-class="router-link-active">
            <i class="pi pi-bookmark"></i> Мои займы
          </router-link>
          <router-link to="/cabinet/reservations" class="nav-link" active-class="router-link-active">
            <i class="pi pi-calendar"></i> Бронирования
          </router-link>
        </template>
      </aside>
      
      <main class="layout-content animate-fade-in">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useUserLayout } from '../composables/useUserLayout'
import Button from 'primevue/button'

const {
  userName,
  menuItems,
  stats,
  loading,
  handleLogout
} = useUserLayout()

// Вспомогательные функции для бейджей в меню
const getMenuItemBadge = (itemId) => {
  if (!stats.value) return null
  if (itemId === 'loans' && stats.value.activeLoans > 0) {
    return stats.value.activeLoans
  }
  if (itemId === 'reservations' && stats.value.unreadNotifications > 0) {
    return stats.value.unreadNotifications
  }
  return null
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
.stat-badge.info {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}
.stat-badge.warning {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.nav-badge {
  margin-left: auto;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}
.nav-badge.info {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

@media (max-width: 1024px) {
  .hidden-sm { display: none; }
}
</style>