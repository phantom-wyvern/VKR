<template>
  <div class="app-wrapper">
    <!-- Ambient background effects -->
    <div class="ambient-glow glow-1"></div>
    <div class="ambient-glow glow-2"></div>
    
    <!-- Main content -->
    <router-view v-slot="{ Component }">
      <transition name="page-fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    
    <!-- Global toast container -->
    <Toast position="bottom-right" :breakpoints="{ '1199px': { width: '90%', right: '5%' } }" />
    
    <!-- Confirmation dialog -->
    <ConfirmDialog group="main" :pt="{
      root: { class: 'glass-elevated' },
      content: { class: 'text-secondary' },
      icon: { class: 'text-primary text-2xl' }
    }" />
  </div>
</template>

<script setup>
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
</script>

<style scoped>
.app-wrapper {
  position: relative;
  min-height: 100vh;
  background: transparent;
  overflow-x: hidden;
}

/* === Ambient Glow Effects === */
.ambient-glow {
  position: fixed;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  pointer-events: none;
  z-index: 0;
  animation: float 20s ease-in-out infinite;
}

.glow-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, var(--primary), transparent 70%);
  top: -200px;
  right: -100px;
}

.glow-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, var(--secondary), transparent 70%);
  bottom: -100px;
  left: -50px;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.05); }
  66% { transform: translate(-20px, 15px) scale(0.95); }
}

/* === Page Transition === */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity var(--transition-normal), transform var(--transition-normal);
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* === Content Layer === */
:deep(.app-wrapper > *:not(.ambient-glow):not(.p-toast)) {
  position: relative;
  z-index: 1;
}
</style>