<template>
  <div class="animate-fade-in checkout-wrapper">
    <div class="page-header mb-6">
      <div>
        <h1 class="page-title">
          <i class="pi pi-sync"></i>
          Выдача и возврат книг
        </h1>
        <p class="page-subtitle">Управление текущими операциями с фондом</p>
      </div>
    </div>

    <div class="settings-grid">
      <!-- Карточка 1: Выдача -->
      <div class="glass settings-card">
        <h3 class="card-header">
          <i class="pi pi-upload" style="color: var(--primary);"></i>
          Выдача книги
        </h3>
        <div class="card-body">
          <div class="form-section">
            <label class="form-label">ID экземпляра</label>
            <InputNumber
              v-model="checkoutForm.copyId"
              placeholder="Введите ID (например: 101)"
              class="w-full"
              :min="1"
              :useGrouping="false"
              :showButtons="false"
            />
          </div>

          <div class="form-section">
            <label class="form-label">ID читателя</label>
            <InputNumber
              v-model="checkoutForm.userId"
              placeholder="Введите ID читателя"
              class="w-full"
              :min="1"
              :useGrouping="false"
              :showButtons="false"
            />
          </div>
          
          <div class="form-section">
            <label class="form-label">Имя читателя</label>
            <InputText 
              v-model="checkoutForm.userName" 
              placeholder="Иванов Иван Иванович" 
              class="w-full" 
            />
          </div>
          
          <div class="info-box mb-4">
            <i class="pi pi-info-circle mr-2"></i>
            <span>ID экземпляра — это ID физической копии книги в базе данных</span>
          </div>

          <Button
            label="Выдать книгу"
            icon="pi pi-check"
            class="w-full mt-4"
            :loading="checkoutLoading"
            @click="handleCheckout"
          />
        </div>
      </div>

      <!-- Карточка 2: Возврат -->
      <div class="glass settings-card">
        <h3 class="card-header">
          <i class="pi pi-download" style="color: var(--secondary);"></i>
          Возврат книги
        </h3>
        <div class="card-body">
          <div class="form-section">
            <label class="form-label">ID экземпляра</label>
            <InputNumber 
              v-model="returnForm.copyId" 
              placeholder="Введите ID для возврата" 
              class="w-full" 
              :showButtons="false"
              @keyup.enter="handleReturn"
            />
          </div>
          
          <div class="info-box mt-4 mb-4">
            <i class="pi pi-info-circle mr-2"></i>
            <span>Введите ID книги на обложке или штрихкоде</span>
          </div>

          <Button 
            label="Принять книгу" 
            icon="pi pi-undo" 
            class="w-full p-button-outlined mt-auto" 
            :loading="returnLoading" 
            @click="handleReturn" 
          />
        </div>
      </div>

      <!-- Карточка 3: Быстрый поиск (на всю ширину) -->
      <div class="glass settings-card full-width">
        <h3 class="card-header">
          <i class="pi pi-search" style="color: var(--warning);"></i>
          Быстрый поиск по штрихкоду
        </h3>
        <div class="card-body">
          <div class="search-wrapper">
            <InputNumber 
              v-model="searchQuery" 
              placeholder="Отсканируйте штрихкод или введите ID экземпляра..." 
              class="search-input" 
              :showButtons="false" 
              @keyup.enter="searchBook" 
            />
            <Button 
              label="Найти" 
              icon="pi pi-search" 
              :loading="searchLoading" 
              @click="searchBook" 
            />
          </div>
          
          <!-- Результат поиска -->
          <transition name="slide-up">
            <div v-if="foundBook" class="search-result mt-6">
              <div class="result-header">
                <div class="result-title-group">
                  <span class="result-icon">📖</span>
                  <h4 class="result-title">{{ foundBook.title }}</h4>
                </div>
                <Tag 
                  :value="foundBook.status === 'available' ? 'Свободна' : 'На руках'" 
                  :severity="foundBook.status === 'available' ? 'success' : 'warning'" 
                />
              </div>
              <div class="result-details">
                <div class="detail-item">
                  <span class="detail-label">Расположение:</span>
                  <span class="detail-value">{{ foundBook.location }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">ID экземпляра:</span>
                  <span class="detail-value mono">{{ foundBook.id }}</span>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useInventoryStore } from '../../stores/inventoryStore'
import { useToast } from 'primevue/usetoast'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'
import Tag from 'primevue/tag'

const store = useInventoryStore()
const toast = useToast()

const checkoutForm = ref({ copyId: null, userId: null, userName: '' })
const returnForm = ref({ copyId: null })
const searchQuery = ref(null)
const foundBook = ref(null)

// Локальные флаги загрузки для кнопок
const checkoutLoading = ref(false)
const returnLoading = ref(false)
const searchLoading = ref(false)

const handleCheckout = async () => {
  const copyId = checkoutForm.value.copyId
  const userId = checkoutForm.value.userId
  const userName = checkoutForm.value.userName?.trim()

  // Проверяем что copyId - валидное число > 0
  const copyIdNum = Number(copyId)
  const userIdNum = Number(userId)
  
  if (!copyIdNum || copyIdNum <= 0 || !userIdNum || userIdNum <= 0 || !userName) {
    toast.add({ severity: 'warn', summary: 'Ошибка ввода', detail: 'Заполните ID экземпляра, ID читателя и имя', life: 3000 })
    return
  }

  checkoutLoading.value = true
  try {
    const result = await store.checkoutBook({
      copyId: copyIdNum,
      userId: userIdNum,
      userName: userName
    })

    if (result.success) {
      toast.add({ severity: 'success', summary: 'Успешно', detail: result.message || 'Книга выдана', life: 3000 })
      checkoutForm.value = { copyId: null, userId: null, userName: '' }
    } else {
      toast.add({ severity: 'error', summary: 'Ошибка', detail: result.message || 'Не удалось выдать книгу', life: 4000 })
    }
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.message || 'Не удалось выдать книгу'
    toast.add({ severity: 'error', summary: 'Ошибка', detail: errorMsg, life: 5000 })
  } finally {
    checkoutLoading.value = false
  }
}

const handleReturn = async () => {
  const copyId = returnForm.value.copyId

  if (!copyId) {
    toast.add({ severity: 'warn', summary: 'Ошибка ввода', detail: 'Введите ID экземпляра', life: 3000 })
    return
  }

  returnLoading.value = true
  try {
    const result = await store.returnBook(Number(copyId))

    if (result.success) {
      toast.add({ severity: 'success', summary: 'Успешно', detail: result.message || 'Книга возвращена', life: 3000 })
      returnForm.value = { copyId: null }
    } else {
      toast.add({ severity: 'error', summary: 'Ошибка', detail: result.message || 'Не удалось принять книгу', life: 4000 })
    }
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.message || 'Не удалось принять книгу'
    toast.add({ severity: 'error', summary: 'Ошибка', detail: errorMsg, life: 5000 })
  } finally {
    returnLoading.value = false
  }
}

const searchBook = async () => {
  if (!searchQuery.value) {
    toast.add({ severity: 'warn', summary: 'Ошибка ввода', detail: 'Введите ID для поиска', life: 3000 })
    return
  }

  searchLoading.value = true
  foundBook.value = null

  try {
    // Имитация задержки поиска (как при запросе к API)
    await new Promise(r => setTimeout(r, 200))
    
    const id = Number(searchQuery.value)
    for (const book of store.books) {
      const copy = book.copies.find(c => c.id === id)
      if (copy) {
        foundBook.value = { ...copy, title: book.title }
        return
      }
    }
    
    toast.add({ severity: 'info', summary: 'Не найдено', detail: 'Экземпляр с таким ID не найден в базе', life: 3000 })
  } finally {
    searchLoading.value = false
  }
}
</script>

<style scoped>
/* Обертка для отступов страницы */
.checkout-wrapper {
  padding: 0 32px 48px !important;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* Сетка карточек */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}
.full-width {
  grid-column: 1 / -1;
}

/* Стили карточки */
.settings-card {
  padding: 24px;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 24px 0;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--glass-border);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
}

/* Поля формы */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

/* Поиск */
.search-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}
.search-wrapper .search-input {
  flex: 1;
}
.search-wrapper .p-inputnumber,
.search-wrapper .p-inputtext {
  width: 100%;
}

/* Результат поиска */
.search-result {
  padding: 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  animation: slideIn 0.3s ease;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--glass-border);
}

.result-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-icon {
  font-size: 24px;
}

.result-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.result-details {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.detail-value {
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 500;
}

.detail-value.mono {
  font-family: monospace;
  color: var(--primary);
}

/* Инфо-блок */
.info-box {
  background: rgba(187, 134, 252, 0.1);
  border: 1px solid rgba(187, 134, 252, 0.2);
  border-radius: 8px;
  padding: 12px;
  font-size: 13px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
}
.info-box i {
  color: var(--primary);
}

/* Анимация */
@keyframes slideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.3s ease;
}
.slide-up-enter-from, .slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Адаптивность */
@media (max-width: 900px) {
  .checkout-wrapper {
    padding: 0 16px 32px !important;
  }
  .settings-grid {
    grid-template-columns: 1fr;
  }
  .search-wrapper {
    flex-direction: column;
  }
  .search-wrapper .p-button {
    width: 100%;
  }
}
</style>