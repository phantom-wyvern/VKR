<template>
  <div class="animate-fade-in">
    <!-- Header & Action Bar -->
    <div class="flex justify-between items-center mb-8 flex-wrap gap-4">
      <div>
        <h1 class="page-title">
          <i class="pi pi-tags" style="color: var(--primary);"></i>
          Жанры книг
        </h1>
        <p class="page-subtitle">Управление справочником жанров</p>
      </div>
      
      <div class="flex gap-3 items-center">
        <InputText 
          v-model="newGenre" 
          placeholder="Новый жанр" 
          class="w-64" 
          @keyup.enter="addGenre"
          :disabled="store.loading"
        />
        <Button 
          label="Добавить" 
          icon="pi pi-plus" 
          :loading="store.loading"
          :disabled="!newGenre.trim()"
          @click="addGenre" 
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading && !store.genres.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка жанров...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ store.error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="loadGenres" />
    </div>

    <!-- Table -->
    <template v-else>
      <div class="table-container">
        <DataTable 
          :value="store.genres" 
          stripedRows 
          class="border-none"
          emptyMessage="Жанры не найдены. Добавьте первый жанр."
        >
          <Column field="id" header="ID" style="width: 80px"></Column>
          <Column field="name" header="Название" sortable></Column>
          <Column header="Действия" style="width: 120px">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-sm p-button-text" 
                  @click="editGenre(data)"
                  title="Редактировать"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-sm p-button-text p-button-danger" 
                  @click="confirmDelete(data)"
                  title="Удалить"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
      
      <!-- Info footer -->
      <div class="text-center text-secondary text-sm mt-4">
        Всего жанров: {{ store.genres.length }}
      </div>
    </template>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="showDeleteDialog" 
      modal 
      header="Подтверждение удаления"
      :style="{ width: '400px' }"
    >
      <p class="mb-4">
        Вы уверены, что хотите удалить жанр <strong>"{{ genreToDelete?.name }}"</strong>?<br>
        <span class="text-secondary text-sm">Это действие нельзя отменить.</span>
      </p>
      <template #footer>
        <Button 
          label="Отмена" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showDeleteDialog = false" 
        />
        <Button 
          label="Удалить" 
          icon="pi pi-trash" 
          class="p-button-danger" 
          :loading="deleting"
          @click="deleteGenre" 
        />
      </template>
    </Dialog>

    <!-- Toast for notifications -->
    <Toast position="top-right" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../../stores/adminStore'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'

const store = useAdminStore()
const toast = useToast()

const newGenre = ref('')
const showDeleteDialog = ref(false)
const genreToDelete = ref(null)
const deleting = ref(false)

onMounted(() => { loadGenres() })

const loadGenres = async () => { await store.loadGenres() }

const addGenre = async () => {
  const name = newGenre.value.trim()
  if (!name) return
  if (store.genres.some(g => g.name.toLowerCase() === name.toLowerCase())) {
    toast.add({ severity: 'warn', summary: 'Уже существует', detail: `Жанр "${name}" уже есть в списке`, life: 3000 })
    return
  }
  const result = await store.addGenre(name)
  if (result.success) {
    toast.add({ severity: 'success', summary: 'Готово', detail: `Жанр "${name}" добавлен`, life: 3000 })
    newGenre.value = ''
  } else {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: result.error || 'Не удалось добавить жанр', life: 4000 })
  }
}

const editGenre = (genre) => {
  const newName = prompt('Новое название жанра:', genre.name)
  if (newName && newName.trim() && newName.trim() !== genre.name) {
    store.updateGenre(genre.id, { name: newName.trim() })
      .then(result => {
        if (result.success) toast.add({ severity: 'success', summary: 'Готово', detail: 'Жанр обновлён', life: 3000 })
      })
  }
}

const confirmDelete = (genre) => {
  genreToDelete.value = genre
  showDeleteDialog.value = true
}

const deleteGenre = async () => {
  if (!genreToDelete.value) return
  deleting.value = true
  const result = await store.deleteGenre(genreToDelete.value.id)
  if (result.success) {
    toast.add({ severity: 'success', summary: 'Удалено', detail: `Жанр "${genreToDelete.value.name}" удалён`, life: 3000 })
    showDeleteDialog.value = false
    genreToDelete.value = null
  } else {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: result.error || 'Не удалось удалить жанр', life: 4000 })
  }
  deleting.value = false
}
</script>