<template>
  <div class="public-layout">
    <!-- Header -->
    <header class="glass public-header">
      <router-link to="/" class="logo-link">
        <div class="logo-icon"><i class="pi pi-book"></i></div>
        <span class="logo-text">Библиотека</span>
      </router-link>
      
      <nav class="nav-links">
        <router-link to="/catalog" class="nav-link">
          <i class="pi pi-search"></i> Каталог
        </router-link>
        <router-link to="/login">
          <Button label="Войти" icon="pi pi-sign-in" class="p-button-sm" />
        </router-link>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="public-main">
      <!-- Лендинг (показывается только на /) -->
      <div v-if="$route.path === '/'" class="landing-wrapper animate-fade-in">
        
        <!-- Состояние загрузки -->
        <div v-if="loading" class="loading-placeholder">
          <i class="pi pi-spin pi-spinner" style="font-size: 3rem; color: var(--primary);"></i>
        </div>

        <template v-else-if="landingData">
          <section class="hero-section">
            <h1 class="hero-title" v-html="landingData.heroTitle"></h1>
            <p class="hero-subtitle">{{ landingData.heroSubtitle }}</p>
            <div class="hero-actions">
              <Button label="Начать работу" icon="pi pi-arrow-right" iconPos="right" @click="$router.push('/register')" />
              <Button label="Смотреть каталог" icon="pi pi-search" class="p-button-outlined" @click="$router.push('/catalog')" />
            </div>
          </section>

          <section class="features-section">
            <div class="features-grid">
              <div 
                v-for="(feat, i) in landingData.features" 
                :key="i" 
                class="glass feature-card"
              >
                <div class="feature-icon" :style="{ background: feat.bg, color: feat.color }">
                  <i :class="feat.icon"></i>
                </div>
                <h3>{{ feat.title }}</h3>
                <p>{{ feat.desc }}</p>
              </div>
            </div>
          </section>
        </template>
      </div>

      <!-- Вложенные маршруты (/login, /register, /catalog и т.д.) -->
      <router-view v-else />
    </main>

    <!-- Footer -->
    <footer class="glass public-footer">
      <p>© {{ currentYear }} Центральная библиотека. Все права защищены.</p>
      <div class="footer-links">
        <a 
          v-for="link in landingData?.footerLinks" 
          :key="link.label" 
          :href="link.url"
        >
          {{ link.label }}
        </a>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchLandingContent } from '../api/landingService'
import Button from 'primevue/button'

const loading = ref(true)
const landingData = ref(null)
const currentYear = new Date().getFullYear()

// Загрузка контента лендинга при монтировании
onMounted(async () => {
  try {
    landingData.value = await fetchLandingContent()
  } catch (error) {
    console.error('Failed to load landing content:', error)
  } finally {
    loading.value = false
  }
})
</script>