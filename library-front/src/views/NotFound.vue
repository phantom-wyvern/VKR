<template>
  <div class="error-page">
    <div class="glass error-card animate-fade-in">
      <div class="error-icon-wrap">
        <i class="pi pi-exclamation-circle"></i>
      </div>
      <h1 class="error-code">404</h1>
      <p class="error-title">Страница не найдена</p>
      <p class="error-subtitle">Возможно, ссылка устарела или адрес был введён с ошибкой.</p>
      
      <router-link to="/">
        <Button label="На главную" icon="pi pi-home" class="p-button-outlined" />
      </router-link>
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'
</script>