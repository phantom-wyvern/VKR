<template>
  <div class="animate-fade-in">
    <h1 class="page-title" style="margin-bottom: 24px;">
      <i class="pi pi-cog" style="color: var(--primary);"></i>
      Настройки системы
    </h1>

    <!-- Loading State -->
    <div v-if="loading" class="glass p-12 text-center mb-6">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка настроек...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="glass p-8 text-center border-red-500/20 border mb-6">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="loadSettingsData" />
    </div>

    <template v-else>
      <div class="settings-grid">
        <!-- Карточка 1: Информация -->
        <div class="glass settings-card">
          <h3 class="card-header"><i class="pi pi-building"></i> Информация о библиотеке</h3>
          <div class="card-body">
            <div class="setting-row"><span class="setting-label">Название</span><InputText v-model="form.libraryName" class="setting-input" placeholder="Центральная библиотека" /></div>
            <div class="setting-row"><span class="setting-label">Email</span><InputText v-model="form.libraryEmail" type="email" class="setting-input" placeholder="info@library.ru" /></div>
            <div class="setting-row"><span class="setting-label">Адрес</span><InputText v-model="form.libraryAddress" class="setting-input" placeholder="ул. Ленина, 1" /></div>
            <div class="setting-row"><span class="setting-label">Телефон</span><InputText v-model="form.libraryPhone" class="setting-input" placeholder="+7 (495) 123-45-67" /></div>
            <div class="setting-row"><span class="setting-label">Начало работы</span><InputText v-model="form.workHoursStart" class="setting-input-compact" placeholder="9:00" /></div>
            <div class="setting-row"><span class="setting-label">Конец работы</span><InputText v-model="form.workHoursEnd" class="setting-input-compact" placeholder="21:00" /></div>
          </div>
        </div>

        <!-- Карточка 2: Правила выдачи -->
        <div class="glass settings-card">
          <h3 class="card-header"><i class="pi pi-book"></i> Правила выдачи</h3>
          <div class="card-body">
            <div class="setting-row"><span class="setting-label">Срок выдачи (дней)</span><InputNumber v-model="form.loanPeriod" class="setting-input-compact" :showButtons="false" /></div>
            <div class="setting-row"><span class="setting-label">Макс. книг на руки</span><InputNumber v-model="form.maxBooksPerUser" class="setting-input-compact" :showButtons="false" /></div>
          </div>
        </div>

        <!-- Карточка 3: Параметры системы -->
        <div class="glass settings-card full-width">
          <h3 class="card-header"><i class="pi pi-sliders-h"></i> Параметры системы</h3>
          <div class="card-body">
            <div class="setting-row">
              <div class="setting-info"><span class="setting-label">Бронирование книг</span><span class="setting-desc">Разрешить читателям бронировать книги</span></div>
              <InputSwitch v-model="form.enableReservations" />
            </div>
            <div class="setting-row">
              <div class="setting-info"><span class="setting-label">Email уведомления</span><span class="setting-desc">Отправлять уведомления на email</span></div>
              <InputSwitch v-model="form.enableEmailNotifications" />
            </div>
          </div>
        </div>
      </div>

      <!-- Кнопки -->
      <div class="flex justify-end gap-3 mt-6">
        <Button label="Сбросить" icon="pi pi-undo" class="p-button-outlined" :loading="saving" @click="resetForm" />
        <Button label="Сохранить" icon="pi pi-check" :loading="saving" @click="saveSettings" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../../stores/adminStore'
import { useToast } from 'primevue/usetoast'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import InputSwitch from 'primevue/inputswitch'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'

const store = useAdminStore()
const toast = useToast()

const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const form = ref({})

// Загрузка при монтировании
onMounted(() => {
  loadSettingsData()
})

const loadSettingsData = async () => {
  loading.value = true
  error.value = null
  try {
    await store.loadSettings()
    // Клонируем, чтобы не мутировать стор напрямую до сохранения
    form.value = { ...store.settings }
  } catch (e) {
    error.value = e.message || 'Не удалось загрузить настройки'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  // Откатываем к состоянию, которое было при загрузке
  form.value = { ...store.settings }
  toast.add({ severity: 'info', summary: 'Сброшено', detail: 'Изменения отменены', life: 2000 })
}

const saveSettings = async () => {
  saving.value = true
  error.value = null
  try {
    const result = await store.saveSettings(form.value)
    if (result.success) {
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Настройки сохранены', life: 3000 })
      // Синхронизируем форму с актуальным состоянием стора (на случай если бэкенд что-то скорректировал)
      form.value = { ...store.settings }
    } else {
      throw new Error(result.error || 'Ошибка сохранения')
    }
  } catch (e) {
    error.value = e.message
    toast.add({ severity: 'error', summary: 'Ошибка', detail: e.message, life: 4000 })
  } finally {
    saving.value = false
  }
}
</script>