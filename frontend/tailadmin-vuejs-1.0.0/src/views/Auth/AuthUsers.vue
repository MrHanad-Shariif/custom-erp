<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Users'" />
    <div class="space-y-5">
      <ComponentCard title="Users">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search users..." class="search-input" />
          <button v-if="canEdit" type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Add User
          </button>
        </div>
        <ErpDataTable
          :columns="columns"
          :data="paginatedUsers"
          :loading="loading"
          empty-text="No users yet."
          :on-edit="canEdit ? openForm : undefined"
          :on-delete="canEdit ? confirmDelete : undefined"
        />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredUsers.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="editingId ? 'Edit User' : 'Add User'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveUser">
      <ErpFormField v-model="form.email" label="Email" type="email" required :disabled="!!editingId" />
      <ErpFormField v-model="form.full_name" label="Full name" required />
      <ErpFormField v-model="form.password" :label="editingId ? 'New password (leave blank to keep)' : 'Password'" type="password" :required="!editingId" />
      <div v-if="editingId">
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Active</label>
        <label class="inline-flex items-center gap-2">
          <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300" />
          <span class="text-sm text-gray-700 dark:text-gray-300">User can sign in</span>
        </label>
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Roles</label>
        <div class="max-h-48 space-y-2 overflow-y-auto rounded-lg border border-gray-200 p-3 dark:border-gray-700">
          <label v-for="r in roles" :key="r.id" class="flex items-center gap-2">
            <input v-model="form.role_ids" type="checkbox" :value="(r as Record<string, unknown>).id" class="rounded border-gray-300" />
            <span class="text-sm text-gray-700 dark:text-gray-300">{{ (r as Record<string, unknown>).name }}</span>
          </label>
          <p v-if="roles.length === 0" class="text-sm text-gray-500">No roles. Create roles in Authentication → Roles.</p>
        </div>
      </div>
    </ErpFormModal>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import ComponentCard from '@/components/common/ComponentCard.vue'
import ErpDataTable from '@/components/erp/ErpDataTable.vue'
import ErpFormModal from '@/components/erp/ErpFormModal.vue'
import ErpFormField from '@/components/erp/ErpFormField.vue'
import ErpPagination from '@/components/erp/ErpPagination.vue'
import { api } from '@/api/client'
import { useAuth } from '@/composables/useAuth'

const { hasPermission, user: currentUser } = useAuth()
const canEdit = computed(() => hasPermission('auth.edit'))

const columns = [
  { key: 'email', label: 'Email' },
  { key: 'full_name', label: 'Full name' },
  { key: 'roles_display', label: 'Roles' },
  { key: 'is_active', label: 'Active', type: 'badge' },
]
const users = ref<Record<string, unknown>[]>([])
const roles = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({
  email: '',
  full_name: '',
  password: '',
  is_active: true,
  role_ids: [] as string[],
})

const roleNamesMap = computed(() => {
  const m: Record<string, string> = {}
  roles.value.forEach((r) => { m[(r as Record<string, unknown>).id as string] = (r as Record<string, unknown>).name as string })
  return m
})

const usersWithRolesDisplay = computed(() =>
  users.value.map((u) => {
    const r = u as Record<string, unknown>
    const ids = (r.role_ids as string[]) || []
    r.roles_display = ids.map((id) => roleNamesMap.value[id] || id).join(', ') || '—'
    return r
  })
)

const filteredUsers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return usersWithRolesDisplay.value
  return usersWithRolesDisplay.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.email, r.full_name, r.roles_display].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / pageSize)))
const paginatedUsers = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredUsers.value.slice(start, start + pageSize)
})

async function fetchUsers() {
  loading.value = true
  const res = await api<unknown[]>('/api/users')
  if (res.status === 'success' && Array.isArray(res.data)) users.value = res.data as Record<string, unknown>[]
  loading.value = false
}

async function fetchRoles() {
  const res = await api<unknown[]>('/api/roles')
  if (res.status === 'success' && Array.isArray(res.data)) roles.value = res.data as Record<string, unknown>[]
}

function openForm(row?: Record<string, unknown>) {
  editingId.value = row ? (row.id as string) : null
  if (row) {
    form.email = String(row.email ?? '')
    form.full_name = String(row.full_name ?? '')
    form.password = ''
    form.is_active = Boolean(row.is_active !== false)
    form.role_ids = [...((row.role_ids as string[]) || [])]
  } else {
    form.email = ''
    form.full_name = ''
    form.password = ''
    form.is_active = true
    form.role_ids = []
  }
  modalOpen.value = true
}

async function saveUser() {
  if (!form.full_name.trim()) return
  if (!editingId.value && !form.email.trim()) return
  if (!editingId.value && !form.password) return
  saving.value = true
  const payload: Record<string, unknown> = {
    full_name: form.full_name.trim(),
    is_active: form.is_active,
    role_ids: form.role_ids,
  }
  if (!editingId.value) {
    payload.email = form.email.trim().toLowerCase()
    payload.password = form.password
  } else if (form.password) {
    payload.password = form.password
  }
  if (editingId.value) {
    const res = await api(`/api/users/${editingId.value}`, { method: 'PUT', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchUsers() }
  } else {
    const res = await api('/api/users', { method: 'POST', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchUsers() }
  }
  saving.value = false
}

async function confirmDelete(row: Record<string, unknown>) {
  if (currentUser.value && row.id === currentUser.value.id) {
    window.alert('You cannot delete your own account.')
    return
  }
  if (!window.confirm('Delete this user? They will no longer be able to sign in.')) return
  const res = await api(`/api/users/${row.id}`, { method: 'DELETE' })
  if (res.status === 'success') await fetchUsers()
}

onMounted(() => { fetchUsers(); fetchRoles() })
</script>

<style scoped>
.search-input {
  height: 2.75rem;
  min-width: 12rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: #1f2937;
  outline: none;
}
:deep(.dark) .search-input {
  border-color: #374151;
  background: #111827;
  color: rgb(255 255 255 / 0.9);
}
</style>
