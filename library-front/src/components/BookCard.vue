<template>
  <article class="book-card" :class="{ 'book-card--list': isListView }">
    <router-link :to="`/book/${book.id}`" class="book-link" :aria-label="`Подробнее о книге: ${book.title}`">
      
      <!-- Cover Image -->
      <div class="book-cover">
        <img 
          :src="book.cover" 
          :alt="`Обложка книги ${book.title}`"
          class="cover-image"
          loading="lazy"
          @error="onImageError"
        />
        <div v-if="computedStatus" class="book-status" :class="`book-status--${computedStatus.class}`">
          {{ computedStatus.label }}
        </div>
      </div>

      <!-- Book Info -->
      <div class="book-info">
        <h3 class="book-title">{{ book.title }}</h3>
        <p class="book-author">{{ book.author }}</p>
        
        <div class="book-meta">
          <span class="meta-item">
            <span class="meta-icon" aria-hidden="true">📅</span>
            {{ book.year }}
          </span>
          <span class="meta-item">
            <span class="meta-icon" aria-hidden="true">📂</span>
            {{ book.genre }}
          </span>
        </div>

        <!-- Copies Info (list view) -->
        <div v-if="isListView && book.copies?.length" class="book-copies">
          <p class="copies-label">Доступно экземпляров:</p>
          <div class="copies-list">
            <span 
              v-for="copy in book.copies" 
              :key="copy.id"
              class="copy-badge"
              :class="`copy-badge--${copy.status}`"
              :title="copy.location"
            >
              {{ copy.status === 'available' ? '✓' : '•' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Action Button (list view) -->
      <div v-if="isListView" class="book-action">
        <Button 
          label="Подробнее" 
          icon="pi pi-eye" 
          class="p-button-sm p-button-outlined"
        />
      </div>
    </router-link>
  </article>
</template>

<script setup>
import { computed, inject } from 'vue'
import { computeBookStatus } from '../api/bookService'
import { FALLBACK_IMAGE } from '../config/constants'
import Button from 'primevue/button'

const props = defineProps({
  book: { type: Object, required: true },
  status: { type: Object, default: null } // Можно переопределить вручную
})

// Получаем режим отображения из контекста (если родитель предоставил)
// Если нет — используем дефолт (можно заменить на использование Pinia store)
const viewMode = inject('viewMode', { value: 'grid' })
const isListView = computed(() => viewMode.value === 'list')

// Вычисляем статус: приоритет у пропса, иначе считаем автоматически
const computedStatus = computed(() => {
  if (props.status) return props.status
  return props.book ? computeBookStatus(props.book) : null
})

const onImageError = (event) => {
  // Используем константу из конфига вместо хардкода
  event.target.src = FALLBACK_IMAGE
}
</script>

<!-- Стили остаются без изменений (они уже оптимизированы) -->
<style scoped>
/* ...твои существующие стили... */
</style>