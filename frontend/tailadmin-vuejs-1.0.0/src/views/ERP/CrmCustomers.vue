<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Customers'" />
    <div class="space-y-5">
      <ComponentCard title="Customers">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search customers..." class="search-input" />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Add Customer
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedCustomers" :loading="loading" empty-text="No customers yet." :on-edit="openForm" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredCustomers.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="editingId ? 'Edit Customer' : 'Add Customer'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveCustomer">
      <ErpFormField v-model="form.name" label="Name" required />
      <ErpFormField v-model="form.code" label="Code" placeholder="Auto if empty" />
      <ErpFormField v-model="form.tax_id" label="Tax ID" />
      <ErpFormField v-model="form.billing_address" label="Billing address" type="textarea" />
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
  { key: 'tax_id', label: 'Tax ID' },
  { key: 'id', label: 'View', type: 'link', toTemplate: '/crm/customers/:id', linkLabel: '360' },
]
const customers = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({ name: '', code: '', tax_id: '', billing_address: '' })
const filteredCustomers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return customers.value
  return customers.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.code, r.name, r.tax_id].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredCustomers.value.length / pageSize)))
const paginatedCustomers = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredCustomers.value.slice(start, start + pageSize)
})

async function fetchCustomers() {
  loading.value = true
  const res = await api<unknown[]>('/api/crm/customers')
  if (res.status === 'success' && Array.isArray(res.data)) customers.value = res.data as Record<string, unknown>[]
  loading.value = false
}

function openForm(row?: Record<string, unknown>) {
  editingId.value = row ? (row.id as string) : null
  if (row) {
    form.name = String(row.name ?? '')
    form.code = String(row.code ?? '')
    form.tax_id = String(row.tax_id ?? '')
    form.billing_address = String(row.billing_address ?? '')
  } else {
    form.name = ''
    form.code = ''
    form.tax_id = ''
    form.billing_address = ''
  }
  modalOpen.value = true
}

async function saveCustomer() {
  if (!form.name.trim()) return
  saving.value = true
  const payload = { name: form.name.trim(), code: form.code.trim() || undefined, tax_id: form.tax_id.trim(), billing_address: form.billing_address.trim() }
  if (editingId.value) {
    const res = await api(`/api/crm/customers/${editingId.value}`, { method: 'PUT', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchCustomers() }
  } else {
    const res = await api('/api/crm/customers', { method: 'POST', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchCustomers() }
  }
  saving.value = false
}

onMounted(fetchCustomers)
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
.input-erp {
  height: 2.75rem;
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  background: transparent;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  color: #1f2937;
  outline: none;
}
:deep(.dark) .input-erp,
:deep(.dark) .search-input {
  border-color: #374151;
  background: #111827;
  color: rgb(255 255 255 / 0.9);
}
</style>
