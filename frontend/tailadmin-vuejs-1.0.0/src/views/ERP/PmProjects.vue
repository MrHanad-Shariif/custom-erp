<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Projects'" />
    <div class="space-y-5">
      <ComponentCard title="Projects">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search projects..." class="search-input" />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Add Project
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedProjects" :loading="loading" empty-text="No projects yet." :on-edit="openForm" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredProjects.length" :page-size="pageSize" @update:page="page = $event" />
        <p class="mt-2 text-sm text-gray-500">Open a project to add milestones and tasks.</p>
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="editingId ? 'Edit Project' : 'Add Project'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveProject">
      <ErpFormField v-model="form.name" label="Name" required />
      <ErpFormField v-model="form.code" label="Code" placeholder="Auto if empty" />
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Status</label>
        <select v-model="form.status" class="input-erp">
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="on_hold">On hold</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Start date</label>
        <input v-model="form.start_date" type="date" class="input-erp date-input" />
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">End date</label>
        <input v-model="form.end_date" type="date" class="input-erp date-input" />
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Customer</label>
        <select v-model="form.customer_id" class="input-erp">
          <option value="">— None —</option>
          <option v-for="c in customers" :key="c.id" :value="c.id">{{ (c as Record<string, unknown>).name }} ({{ (c as Record<string, unknown>).code }})</option>
        </select>
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

const columns = [
  { key: 'code', label: 'Code' },
  { key: 'name', label: 'Name' },
  { key: 'status', label: 'Status', type: 'badge' },
  { key: 'start_date', label: 'Start' },
  { key: 'end_date', label: 'End' },
  { key: 'id', label: 'View', type: 'link', toTemplate: '/pm/projects/:id', linkLabel: 'Open' },
]
const projects = ref<Record<string, unknown>[]>([])
const customers = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({ name: '', code: '', status: 'active', start_date: '', end_date: '', customer_id: '' })
const filteredProjects = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return projects.value
  return projects.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.code, r.name, r.status].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredProjects.value.length / pageSize)))
const paginatedProjects = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredProjects.value.slice(start, start + pageSize)
})

async function fetchProjects() {
  loading.value = true
  const res = await api<unknown[]>('/api/pm/projects')
  if (res.status === 'success' && Array.isArray(res.data)) projects.value = res.data as Record<string, unknown>[]
  loading.value = false
}

async function fetchCustomers() {
  const res = await api<unknown[]>('/api/crm/customers')
  if (res.status === 'success' && Array.isArray(res.data)) customers.value = res.data as Record<string, unknown>[]
}

function openForm(row?: Record<string, unknown>) {
  editingId.value = row ? (row.id as string) : null
  if (row) {
    form.name = String(row.name ?? '')
    form.code = String(row.code ?? '')
    form.status = String(row.status ?? 'active')
    form.start_date = row.start_date ? String(row.start_date).slice(0, 10) : ''
    form.end_date = row.end_date ? String(row.end_date).slice(0, 10) : ''
    form.customer_id = String(row.customer_id ?? '')
  } else {
    form.name = ''
    form.code = ''
    form.status = 'active'
    form.start_date = ''
    form.end_date = ''
    form.customer_id = ''
  }
  modalOpen.value = true
}

async function saveProject() {
  if (!form.name.trim()) return
  saving.value = true
  const payload = {
    name: form.name.trim(),
    code: form.code.trim() || undefined,
    status: form.status,
    start_date: form.start_date || undefined,
    end_date: form.end_date || undefined,
    customer_id: form.customer_id || undefined,
  }
  if (editingId.value) {
    const res = await api(`/api/pm/projects/${editingId.value}`, { method: 'PUT', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchProjects() }
  } else {
    const res = await api('/api/pm/projects', { method: 'POST', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchProjects() }
  }
  saving.value = false
}

onMounted(() => { fetchProjects(); fetchCustomers() })
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
.input-erp,
.date-input {
  height: 2.75rem;
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  background: transparent;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  color: #1f2937;
  outline: none;
  cursor: pointer;
}
:deep(.dark) .input-erp,
:deep(.dark) .date-input,
:deep(.dark) .search-input {
  border-color: #374151;
  background: #111827;
  color: rgb(255 255 255 / 0.9);
}
</style>
