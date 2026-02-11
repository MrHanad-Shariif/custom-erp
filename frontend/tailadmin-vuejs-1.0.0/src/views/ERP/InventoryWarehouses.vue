<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Warehouses'" />
    <div class="space-y-5">
      <ComponentCard title="Warehouses">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search warehouses..." class="search-input" />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Add Warehouse
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedWarehouses" :loading="loading" empty-text="No warehouses yet." :on-edit="openForm" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredWarehouses.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="editingId ? 'Edit Warehouse' : 'Add Warehouse'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveWarehouse">
      <ErpFormField v-model="form.name" label="Name" required />
      <ErpFormField v-model="form.code" label="Code" placeholder="Auto if empty" />
      <ErpFormField v-model="form.address" label="Address" type="textarea" />
      <div class="flex items-center gap-2">
        <input type="checkbox" v-model="form.is_default" id="default" class="rounded border-gray-300" />
        <label for="default" class="text-sm text-gray-700 dark:text-gray-300">Default warehouse</label>
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
  { key: 'address', label: 'Address' },
  { key: 'is_default', label: 'Default', type: 'badge' },
]
const warehouses = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({ name: '', code: '', address: '', is_default: false })
const filteredWarehouses = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return warehouses.value
  return warehouses.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.code, r.name, r.address].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredWarehouses.value.length / pageSize)))
const paginatedWarehouses = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredWarehouses.value.slice(start, start + pageSize)
})

async function fetchWarehouses() {
  loading.value = true
  const res = await api<unknown[]>('/api/inventory/warehouses')
  if (res.status === 'success' && Array.isArray(res.data)) warehouses.value = res.data as Record<string, unknown>[]
  loading.value = false
}

function openForm(row?: Record<string, unknown>) {
  editingId.value = row ? (row.id as string) : null
  if (row) {
    form.name = String(row.name ?? '')
    form.code = String(row.code ?? '')
    form.address = String(row.address ?? '')
    form.is_default = Boolean(row.is_default)
  } else {
    form.name = ''
    form.code = ''
    form.address = ''
    form.is_default = false
  }
  modalOpen.value = true
}

async function saveWarehouse() {
  if (!form.name.trim()) return
  saving.value = true
  const payload = { name: form.name.trim(), code: form.code.trim() || undefined, address: form.address.trim(), is_default: form.is_default }
  if (editingId.value) {
    const res = await api(`/api/inventory/warehouses/${editingId.value}`, { method: 'PUT', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchWarehouses() }
  } else {
    const res = await api('/api/inventory/warehouses', { method: 'POST', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchWarehouses() }
  }
  saving.value = false
}

onMounted(fetchWarehouses)
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
