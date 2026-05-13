import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Ripple from 'primevue/ripple'

// Material Dark Theme
import 'primevue/resources/themes/lara-dark-indigo/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'

import './style.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/authStore'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Инициализация аутентификации до старта роутера
const auth = useAuthStore()
await auth.init()

app.use(router)

// PrimeVue с настройками под Material Design
app.use(PrimeVue, {
  ripple: true,
  inputStyle: 'filled', // Material-style filled inputs
  pt: {
    // Global component overrides for dark theme
    button: {
      root: {
        class: 'p-ripple'
      }
    },
    inputtext: {
      root: {
        class: 'transition-all duration-200'
      }
    },
    datatable: {
      root: {
        class: 'overflow-hidden'
      }
    }
  }
})

app.use(ToastService)
app.use(ConfirmationService)

// Global directive for ripple effect
app.directive('ripple', Ripple)

app.mount('#app')