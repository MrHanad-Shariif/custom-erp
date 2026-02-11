<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Invoices'" />
    <div class="space-y-5">
      <ComponentCard title="Invoices">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search invoices..." class="search-input" />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Add Invoice
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedInvoices" :loading="loading" empty-text="No invoices yet." :on-edit="openForm" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredInvoices.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="editingId ? 'Edit Invoice' : 'Add Invoice'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveInvoice">
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Customer *</label>
        <select v-model="form.customer_id" class="input-erp" required>
          <option value="">Select customer</option>
          <option v-for="c in customers" :key="c.id" :value="c.id">{{ (c as Record<string, unknown>).name }} ({{ (c as Record<string, unknown>).code }})</option>
        </select>
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Project</label>
        <select v-model="form.project_id" class="input-erp">
          <option value="">— None —</option>
          <option v-for="p in projects" :key="p.id" :value="p.id">{{ (p as Record<string, unknown>).name }}</option>
        </select>
      </div>
      <ErpFormField v-model="form.amount" label="Amount" type="number" required />
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Due date</label>
        <input v-model="form.due_date" type="date" class="input-erp date-input" />
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Status</label>
        <select v-model="form.status" class="input-erp">
          <option value="draft">Draft</option>
          <option value="sent">Sent</option>
          <option value="paid">Paid</option>
          <option value="overdue">Overdue</option>
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
  { key: 'number', label: 'Number' },
  { key: 'customer_name', label: 'Customer' },
  { key: 'amount', label: 'Amount' },
  { key: 'due_date', label: 'Due date' },
  { key: 'status', label: 'Status', type: 'badge' },
]
const invoices = ref<Record<string, unknown>[]>([])
const customers = ref<Record<string, unknown>[]>([])
const projects = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({ customer_id: '', project_id: '', amount: '', due_date: '', status: 'draft' })

function customerName(id: unknown): string {
  if (!id) return '—'
  const c = customers.value.find((x) => (x as Record<string, unknown>).id === id) as Record<string, unknown> | undefined
  return (c?.name ?? c?.code ?? id) as string
}

const displayInvoices = computed(() =>
  invoices.value.map((inv) => ({
    ...inv,
    customer_name: customerName((inv as Record<string, unknown>).customer_id),
  }))
)
const filteredInvoices = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return displayInvoices.value
  return displayInvoices.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.number, r.customer_name, r.status, r.amount].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredInvoices.value.length / pageSize)))
const paginatedInvoices = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredInvoices.value.slice(start, start + pageSize)
})

async function fetchInvoices() {
  loading.value = true
  const res = await api<unknown[]>('/api/finance/invoices')
  if (res.status === 'success' && Array.isArray(res.data)) invoices.value = res.data as Record<string, unknown>[]
  loading.value = false
}

async function fetchCustomers() {
  const res = await api<unknown[]>('/api/crm/customers')
  if (res.status === 'success' && Array.isArray(res.data)) customers.value = res.data as Record<string, unknown>[]
}

async function fetchProjects() {
  const res = await api<unknown[]>('/api/pm/projects')
  if (res.status === 'success' && Array.isArray(res.data)) projects.value = res.data as Record<string, unknown>[]
}

function openForm(row?: Record<string, unknown>) {
  editingId.value = row ? (row.id as string) : null
  if (row) {
    form.customer_id = String(row.customer_id ?? '')
    form.project_id = String(row.project_id ?? '')
    form.amount = String(row.amount ?? '')
    form.due_date = row.due_date ? String(row.due_date).slice(0, 10) : ''
    form.status = String(row.status ?? 'draft')
  } else {
    form.customer_id = ''
    form.project_id = ''
    form.amount = ''
    form.due_date = ''
    form.status = 'draft'
  }
  modalOpen.value = true
}

async function saveInvoice() {
  if (!form.customer_id) return
  saving.value = true
  const payload = {
    customer_id: form.customer_id,
    project_id: form.project_id || undefined,
    amount: Number(form.amount) || 0,
    due_date: form.due_date || undefined,
    status: form.status,
  }
  if (editingId.value) {
    const res = await api(`/api/finance/invoices/${editingId.value}`, { method: 'PUT', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchInvoices() }
  } else {
    const res = await api('/api/finance/invoices', { method: 'POST', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchInvoices() }
  }
  saving.value = false
}

onMounted(() => { fetchInvoices(); fetchCustomers(); fetchProjects() })
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
