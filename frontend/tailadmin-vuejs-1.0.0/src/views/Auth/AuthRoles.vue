<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Roles & Permissions'" />
    <div class="space-y-5">
      <ComponentCard title="Roles">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search roles..." class="search-input" />
          <button v-if="canEdit" type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Add Role
          </button>
        </div>
        <ErpDataTable
          :columns="columns"
          :data="paginatedRoles"
          :loading="loading"
          empty-text="No roles yet."
          :on-edit="canEdit ? openForm : undefined"
          :on-delete="canEdit ? confirmDelete : undefined"
        />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredRoles.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="editingId ? 'Edit Role' : 'Add Role'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveRole">
      <ErpFormField v-model="form.name" label="Role name" required />
      <ErpFormField v-model="form.description" label="Description" type="textarea" placeholder="Optional" />
      <div>
        <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-400">Permissions</label>
        <div class="max-h-64 space-y-3 overflow-y-auto rounded-lg border border-gray-200 p-3 dark:border-gray-700">
          <div v-for="group in permissionsByModule" :key="group.module" class="space-y-1.5">
            <p class="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">{{ group.module }}</p>
            <div class="flex flex-wrap gap-x-4 gap-y-1">
              <label v-for="p in group.permissions" :key="p.id" class="inline-flex items-center gap-2">
                <input v-model="form.permission_ids" type="checkbox" :value="p.id" class="rounded border-gray-300" />
                <span class="text-sm text-gray-700 dark:text-gray-300">{{ p.action }}</span>
              </label>
            </div>
          </div>
          <p v-if="permissions.length === 0" class="text-sm text-gray-500">No permissions defined.</p>
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

const { hasPermission } = useAuth()
const canEdit = computed(() => hasPermission('auth.edit'))

const columns = [
  { key: 'name', label: 'Role' },
  { key: 'description', label: 'Description' },
  { key: 'permissions_display', label: 'Permissions' },
]
const roles = ref<Record<string, unknown>[]>([])
const permissions = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({
  name: '',
  description: '',
  permission_ids: [] as string[],
})

const permissionsByModule = computed(() => {
  const list = permissions.value as { id: string; module: string; action: string }[]
  const byModule: Record<string, { id: string; module: string; action: string }[]> = {}
  list.forEach((p) => {
    if (!byModule[p.module]) byModule[p.module] = []
    byModule[p.module].push(p)
  })
  return Object.entries(byModule).map(([module, perms]) => ({ module, permissions: perms }))
})

const rolesWithPermissionsDisplay = computed(() =>
  roles.value.map((r) => {
    const row = r as Record<string, unknown>
    const permIds = (row.permission_ids as string[]) || []
    const permList = permissions.value as { id: string; action: string }[]
    row.permissions_display = permIds.map((id) => permList.find((p) => p.id === id)?.action ?? id).join(', ') || '—'
    return row
  })
)



const filteredRoles = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return rolesWithPermissionsDisplay.value
  return rolesWithPermissionsDisplay.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.name, r.description, r.permissions_display].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRoles.value.length / pageSize)))
const paginatedRoles = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredRoles.value.slice(start, start + pageSize)
})

async function fetchRoles() {
  loading.value = true
  const res = await api<unknown[]>('/api/roles')
  if (res.status === 'success' && Array.isArray(res.data)) roles.value = res.data as Record<string, unknown>[]
  loading.value = false
}

async function fetchPermissions() {
  const res = await api<unknown[]>('/api/roles/permissions')
  if (res.status === 'success' && Array.isArray(res.data)) permissions.value = res.data as Record<string, unknown>[]
}

function openForm(row?: Record<string, unknown>) {
  if (row) {
    editingId.value = row.id as string
    form.name = String(row.name ?? '')
    form.description = String(row.description ?? '')
    form.permission_ids = [...((row.permission_ids as string[]) || [])]
  } else {
    editingId.value = null
    form.name = ''
    form.description = ''
    form.permission_ids = []
  }
  modalOpen.value = true
}

async function saveRole() {
  if (!form.name.trim()) return
  saving.value = true
  const payload = { name: form.name.trim(), description: form.description.trim(), permission_ids: form.permission_ids }
  if (editingId.value) {
    const res = await api(`/api/roles/${editingId.value}`, { method: 'PUT', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchRoles() }
  } else {
    const res = await api('/api/roles', { method: 'POST', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchRoles() }
  }
  saving.value = false
}

async function confirmDelete(row: Record<string, unknown>) {
  if (!window.confirm('Delete this role? Users with this role will lose these permissions.')) return
  const res = await api(`/api/roles/${row.id}`, { method: 'DELETE' })
  if (res.status === 'success') await fetchRoles()
}

onMounted(() => { fetchRoles(); fetchPermissions() })
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
