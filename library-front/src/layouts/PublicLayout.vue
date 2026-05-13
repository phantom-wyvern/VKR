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
        <section class="hero-section">
          <h1 class="hero-title">Библиотека <span class="gradient-text">нового поколения</span></h1>
          <p class="hero-subtitle">
            Мгновенный поиск, удобное бронирование и полный контроль над вашими займами. 
            Присоединяйтесь к цифровой экосистеме чтения.
          </p>
          <div class="hero-actions">
            <Button label="Начать работу" icon="pi pi-arrow-right" iconPos="right" @click="$router.push('/register')" />
            <Button label="Смотреть каталог" icon="pi pi-search" class="p-button-outlined" @click="$router.push('/catalog')" />
          </div>
        </section>

        <section class="features-section">
          <div class="features-grid">
            <div v-for="(feat, i) in features" :key="i" class="glass feature-card">
              <div class="feature-icon" :style="{ background: feat.bg, color: feat.color }">
                <i :class="feat.icon"></i>
              </div>
              <h3>{{ feat.title }}</h3>
              <p>{{ feat.desc }}</p>
            </div>
          </div>
        </section>
      </div>

      <!-- Вложенные маршруты (/login, /register, /catalog и т.д.) -->
      <router-view v-else />
    </main>

    <!-- Footer -->
    <footer class="glass public-footer">
      <p>© {{ new Date().getFullYear() }} Центральная библиотека. Все права защищены.</p>
      <div class="footer-links">
        <a href="#">О нас</a>
        <a href="#">Контакты</a>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Button from 'primevue/button'

const features = [
  {
    icon: 'pi pi-search',
    title: 'Умный поиск',
    desc: 'Находите книги за секунды по автору, жанру или ISBN. Фильтрация по статусу наличия.',
    bg: 'rgba(187, 134, 252, 0.15)',
    color: '#bb86fc'
  },
  {
    icon: 'pi pi-calendar-plus',
    title: 'Онлайн бронь',
    desc: 'Забронируйте книгу в один клик. Система уведомит вас, когда она будет готова к выдаче.',
    bg: 'rgba(3, 218, 198, 0.15)',
    color: '#03dac6'
  },
  {
    icon: 'pi pi-chart-bar',
    title: 'Ваш профиль',
    desc: 'История чтений, активные займы и статистика — всё в личном кабинете.',
    bg: 'rgba(239, 68, 68, 0.15)',
    color: '#ef4444'
  }
]
</script>