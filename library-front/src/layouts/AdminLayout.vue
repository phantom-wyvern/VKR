<template>
  <div class="app-layout">
    <!-- Header -->
    <header class="glass layout-header">
      <router-link to="/admin" class="logo-btn">
        <div class="icon-wrap">
          <i class="pi pi-shield"></i>
        </div>
        <span>Админ-панель</span>
      </router-link>

      <div class="user-header">
        <!-- Показываем имя из композабла (с загрузкой) -->
        <span v-if="loading" class="user-name text-secondary">Загрузка...</span>
        <span v-else class="user-name">{{ userName }}</span>
        
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
        <!-- Рендерим меню динамически из композабла -->
        <template v-if="menuItems.length">
          <router-link 
            v-for="item in menuItems" 
            :key="item.id"
            :to="item.path" 
            class="nav-link" 
            active-class="router-link-active"
          >
            <i :class="item.icon"></i> {{ item.label }}
          </router-link>
        </template>
        
        <!-- Фолбэк: статическое меню, если моки не загрузились -->
        <template v-else>
          <router-link to="/admin" class="nav-link" active-class="router-link-active">
            <i class="pi pi-chart-bar"></i> Обзор
          </router-link>
          <router-link to="/admin/users" class="nav-link" active-class="router-link-active">
            <i class="pi pi-users"></i> Пользователи
          </router-link>
          <router-link to="/admin/settings" class="nav-link" active-class="router-link-active">
            <i class="pi pi-cog"></i> Настройки
          </router-link>
          <router-link to="/admin/genres" class="nav-link" active-class="router-link-active">
            <i class="pi pi-tags"></i> Жанры
          </router-link>
          <router-link to="/admin/audit" class="nav-link" active-class="router-link-active">
            <i class="pi pi-history"></i> Аудит
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
import { useAdminLayout } from '../composables/useAdminLayout'
import Button from 'primevue/button'

// Используем композабл вместо прямого доступа к стору
const { userName, userRole, menuItems, loading, handleLogout, checkPermission } = useAdminLayout()
</script>