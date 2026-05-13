<template>
  <div class="animate-fade-in">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8 flex-wrap gap-4">
      <div>
        <h1 class="page-title">
          <i class="pi pi-users" style="color: var(--primary);"></i>
          Управление пользователями
        </h1>
        <p class="page-subtitle">Добавление, редактирование и блокировка аккаунтов</p>
      </div>
      <Button label="Добавить пользователя" icon="pi pi-user-plus" @click="openCreateDialog" />
    </div>

    <!-- Loading/Error States -->
    <div v-if="store.loading && !store.users.length" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Загрузка пользователей...</p>
    </div>
    <div v-else-if="store.error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ store.error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="loadUsers" />
    </div>

    <template v-else>
      <!-- Table -->
      <div class="table-container">
        <DataTable 
          :value="store.users" 
          stripedRows 
          responsiveLayout="scroll" 
          paginator 
          :rows="10"
          :loading="store.loading"
          class="border-none"
          emptyMessage="Пользователи не найдены"
        >
          <Column field="name" header="Имя" sortable></Column>
          <Column field="email" header="Email" sortable></Column>
          <Column field="role" header="Роль" sortable>
            <template #body="{ data }">
              <Tag :value="getRoleName(data.role)" 
                   :severity="data.role === 'admin' ? 'danger' : data.role === 'librarian' ? 'info' : 'success'" />
            </template>
          </Column>
          <Column field="status" header="Статус" sortable>
            <template #body="{ data }">
              <Tag :value="data.status === 'active' ? 'Активен' : 'Заблокирован'" 
                   :severity="data.status === 'active' ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column field="createdAt" header="Дата регистрации" sortable>
            <template #body="{ data }">{{ formatDate(data.createdAt) }}</template>
          </Column>
          <Column header="Действия" style="width: 220px">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button icon="pi pi-pencil" class="p-button-sm p-button-text" @click="openEditDialog(data)" title="Редактировать" />
                <Button :icon="data.status === 'active' ? 'pi pi-lock' : 'pi pi-unlock'"
                        :class="['p-button-sm p-button-text', data.status === 'active' ? 'p-button-warning' : 'p-button-success']"
                        @click="toggleUserStatus(data)"
                        :title="data.status === 'active' ? 'Заблокировать' : 'Разблокировать'" />
                <Button icon="pi pi-trash" class="p-button-sm p-button-text p-button-danger"
                        @click="confirmDelete(data)"
                        :disabled="data.role === 'admin'"
                        title="Удалить" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </template>

    <!-- Add/Edit Dialog -->
    <Dialog v-model:visible="showDialog" modal :header="editingUser ? 'Редактировать пользователя' : 'Добавить пользователя'" :style="{ width: '500px' }">
      <div class="flex flex-col gap-4 py-2">
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-2">Имя</label>
          <InputText v-model="form.name" class="w-full" placeholder="Иван Иванов" :disabled="saving" />
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-2">Email</label>
          <InputText v-model="form.email" type="email" class="w-full" placeholder="example@mail.ru" :disabled="saving" />
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-2">Роль</label>
          <Dropdown v-model="form.role" :options="roles" optionLabel="label" optionValue="value" class="w-full" :disabled="saving" />
        </div>
      </div>
      <template #footer>
        <Button label="Отмена" icon="pi pi-times" class="p-button-text" @click="closeDialog" :disabled="saving" />
        <Button label="Сохранить" icon="pi pi-check" :loading="saving" @click="saveUser" />
      </template>
    </Dialog>

    <Toast position="top-right" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../../stores/adminStore'
import { useToast } from 'primevue/usetoast'
import { formatDate, getRoleName } from '../../utils/formatters'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'

const store = useAdminStore()
const toast = useToast()

const showDialog = ref(false)
const editingUser = ref(null)
const saving = ref(false)
const form = ref({ name: '', email: '', role: 'reader' })

const roles = [
  { label: 'Читатель', value: 'reader' },
  { label: 'Библиотекарь', value: 'librarian' },
  { label: 'Администратор', value: 'admin' }
]

// Загрузка при монтировании
onMounted(() => {
  loadUsers()
})

const loadUsers = async () => {
  await store.loadUsers()
}

const openCreateDialog = () => {
  editingUser.value = null
  form.value = { name: '', email: '', role: 'reader' }
  showDialog.value = true
}

const openEditDialog = (user) => {
  editingUser.value = user
  form.value = { name: user.name, email: user.email, role: user.role }
  showDialog.value = true
}

const saveUser = async () => {
  if (!form.value.name.trim() || !form.value.email.trim()) {
    toast.add({ severity: 'warn', summary: 'Ошибка', detail: 'Заполните имя и email', life: 3000 })
    return
  }

  saving.value = true
  try {
    const result = editingUser.value 
      ? await store.updateUser(editingUser.value.id, form.value)
      : await store.createUser(form.value)

    if (result.success) {
      toast.add({ severity: 'success', summary: 'Успешно', detail: editingUser.value ? 'Пользователь обновлён' : 'Пользователь создан', life: 3000 })
      closeDialog()
    } else {
      throw new Error(result.error || 'Ошибка сохранения')
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: e.message, life: 4000 })
  } finally {
    saving.value = false
  }
}

const toggleUserStatus = async (user) => {
  const action = user.status === 'active' ? 'заблокировать' : 'разблокировать'
  if (!confirm(`Вы уверены, что хотите ${action} пользователя "${user.name}"?`)) return

  try {
    const result = await store.toggleUserStatus(user.id)
    if (result.success) {
      toast.add({ severity: 'success', summary: 'Готово', detail: `Пользователь ${action}`, life: 3000 })
    } else {
      throw new Error(result.error)
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: e.message, life: 4000 })
  }
}

const confirmDelete = async (user) => {
  if (!confirm(`Удалить пользователя "${user.name}"? Это действие нельзя отменить.`)) return
  try {
    const result = await store.deleteUser(user.id)
    if (result.success) {
      toast.add({ severity: 'success', summary: 'Удалено', detail: 'Пользователь удалён', life: 3000 })
    } else {
      throw new Error(result.error)
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: e.message, life: 4000 })
  }
}

const closeDialog = () => {
  showDialog.value = false
  editingUser.value = null
  form.value = { name: '', email: '', role: 'reader' }
}
</script>