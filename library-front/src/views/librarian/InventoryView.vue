<template>
  <div class="animate-fade-in">
    <div class="page-header">
      <h1 class="page-title">
        <i class="pi pi-book" style="color: var(--primary);"></i>
        Управление фондом
      </h1>
      <Button label="Добавить книгу" icon="pi pi-plus" @click="showAddDialog = true" />
    </div>

    <div class="table-container">
      <DataTable :value="store.books" stripedRows responsiveLayout="scroll" class="border-none">
        <Column field="title" header="Название" sortable></Column>
        <Column field="author" header="Автор" sortable></Column>
        <Column field="year" header="Год" sortable style="width: 80px"></Column>
        <Column field="genre" header="Жанр" sortable></Column>
        <Column field="isbn" header="ISBN" style="width: 150px"></Column>
        <Column header="Экземпляров" style="width: 100px">
          <template #body="{ data }">
            <Tag :value="data.copies.length" severity="info" />
          </template>
        </Column>
        <Column header="Действия" style="width: 120px">
          <template #body="{ data }">
            <div class="action-buttons">
              <Button icon="pi pi-pencil" class="p-button-sm p-button-text" @click="editBook(data)" />
              <Button icon="pi pi-trash" class="p-button-sm p-button-text p-button-danger" @click="deleteBook(data.id)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

        <Dialog v-model:visible="showAddDialog" modal :header="bookForm.id ? 'Редактировать книгу' : 'Добавить книгу'" :style="{ width: '500px' }">
      <div class="flex flex-col gap-4 py-2">
        <div>
          <label>Название</label>
          <InputText v-model="bookForm.title" class="w-full" />
        </div>
        <div>
          <label>Автор</label>
          <InputText v-model="bookForm.author" class="w-full" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label>Год</label>
            <InputNumber v-model="bookForm.year" class="w-full" useGrouping="false" />
          </div>
          <div>
            <label>Жанр</label>
            <InputText v-model="bookForm.genre" class="w-full" />
          </div>
        </div>
        <div>
          <label>ISBN</label>
          <InputText v-model="bookForm.isbn" class="w-full" />
        </div>
        <div>
          <label>Описание</label>
          <!-- rows="4" делает поле высоким -->
          <Textarea v-model="bookForm.description" rows="4" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Отмена" icon="pi pi-times" class="p-button-text" @click="showAddDialog = false" />
        <Button label="Сохранить" icon="pi pi-check" @click="saveBook" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useInventoryStore } from '../../stores/inventoryStore'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'

const store = useInventoryStore()
const showAddDialog = ref(false)
const bookForm = ref({ id: null, title: '', author: '', year: 2024, genre: '', isbn: '', description: '' })

const editBook = (book) => { bookForm.value = { ...book }; showAddDialog.value = true }
const saveBook = async () => { if (bookForm.value.id) await store.updateBook(bookForm.value.id, bookForm.value); else await store.addBook(bookForm.value); showAddDialog.value = false; bookForm.value = { id: null, title: '', author: '', year: 2024, genre: '', isbn: '', description: '' } }
const deleteBook = async (id) => { if (confirm('Удалить книгу?')) await store.deleteBook(id) }
</script>