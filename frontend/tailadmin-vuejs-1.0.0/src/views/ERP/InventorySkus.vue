<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'SKUs'" />
    <div class="space-y-5">
      <ComponentCard title="SKUs (Products)">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search SKUs..." class="search-input" />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Add SKU
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedSkus" :loading="loading" empty-text="No SKUs yet." :on-edit="openForm" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredSkus.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="editingId ? 'Edit SKU' : 'Add SKU'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveSku">
      <ErpFormField v-model="form.name" label="Name" required />
      <ErpFormField v-model="form.code" label="Code" placeholder="Auto if empty" />
      <ErpFormField v-model="form.unit" label="Unit" placeholder="unit" />
      <ErpFormField v-model="form.reorder_point" label="Reorder point" type="number" />
      <ErpFormField v-model="form.reorder_quantity" label="Reorder quantity" type="number" />
      <div class="flex items-center gap-2">
        <input type="checkbox" v-model="form.is_active" id="active" class="rounded border-gray-300" />
        <label for="active" class="text-sm text-gray-700 dark:text-gray-300">Active</label>
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
  { key: 'unit', label: 'Unit' },
  { key: 'reorder_point', label: 'Reorder point' },
  { key: 'reorder_quantity', label: 'Reorder qty' },
  { key: 'is_active', label: 'Active', type: 'badge' },
]
const skus = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({ name: '', code: '', unit: 'unit', reorder_point: '0', reorder_quantity: '0', is_active: true })
const filteredSkus = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return skus.value
  return skus.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.code, r.name, r.unit].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredSkus.value.length / pageSize)))
const paginatedSkus = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredSkus.value.slice(start, start + pageSize)
})

async function fetchSkus() {
  loading.value = true
  const res = await api<unknown[]>('/api/inventory/skus')
  if (res.status === 'success' && Array.isArray(res.data)) skus.value = res.data as Record<string, unknown>[]
  loading.value = false
}

function openForm(row?: Record<string, unknown>) {
  editingId.value = row ? (row.id as string) : null
  if (row) {
    form.name = String(row.name ?? '')
    form.code = String(row.code ?? '')
    form.unit = String(row.unit ?? 'unit')
    form.reorder_point = String(row.reorder_point ?? '0')
    form.reorder_quantity = String(row.reorder_quantity ?? '0')
    form.is_active = Boolean(row.is_active)
  } else {
    form.name = ''
    form.code = ''
    form.unit = 'unit'
    form.reorder_point = '0'
    form.reorder_quantity = '0'
    form.is_active = true
  }
  modalOpen.value = true
}

async function saveSku() {
  if (!form.name.trim()) return
  saving.value = true
  const payload = {
    name: form.name.trim(),
    code: form.code.trim() || undefined,
    unit: form.unit.trim(),
    reorder_point: Number(form.reorder_point) || 0,
    reorder_quantity: Number(form.reorder_quantity) || 0,
    is_active: form.is_active,
  }
  if (editingId.value) {
    const res = await api(`/api/inventory/skus/${editingId.value}`, { method: 'PUT', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchSkus() }
  } else {
    const res = await api('/api/inventory/skus', { method: 'POST', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchSkus() }
  }
  saving.value = false
}

onMounted(fetchSkus)
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
