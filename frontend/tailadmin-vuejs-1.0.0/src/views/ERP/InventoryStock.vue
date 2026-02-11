<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Stock levels'" />
    <div class="space-y-5">
      <ComponentCard title="Stock by warehouse">
        <p class="mb-4 text-sm text-gray-500 dark:text-gray-400">Set or view quantity and reorder point per warehouse + SKU. Use Add to create/update a stock level.</p>
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search stock..." class="search-input" />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Set stock level
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedStock" :loading="loading" empty-text="No stock levels. Create warehouses and SKUs first, then set stock." :show-actions="false" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredStock.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="'Set stock level'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveStock">
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Warehouse *</label>
        <select v-model="form.warehouse_id" class="input-erp" required>
          <option value="">Select warehouse</option>
          <option v-for="w in warehouses" :key="String(w.id)" :value="w.id">{{ w.name }} ({{ w.code }})</option>
        </select>
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">SKU *</label>
        <select v-model="form.sku_id" class="input-erp" required>
          <option value="">Select SKU</option>
          <option v-for="s in skus" :key="String(s.id)" :value="s.id">{{ s.name }} ({{ s.code }})</option>
        </select>
      </div>
      <ErpFormField v-model="form.quantity" label="Quantity" type="number" required />
      <ErpFormField v-model="form.reorder_point" label="Reorder point" type="number" />
    </ErpFormModal>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import ComponentCard from '@/components/common/ComponentCard.vue'
import ErpDataTable from '@/components/erp/ErpDataTable.vue'
import ErpFormModal from '@/components/erp/ErpFormModal.vue'
import ErpFormField from '@/components/erp/ErpFormField.vue'
import ErpPagination from '@/components/erp/ErpPagination.vue'
import { api } from '@/api/client'

const columns = [
  { key: 'warehouse_name', label: 'Warehouse' },
  { key: 'sku_name', label: 'SKU' },
  { key: 'quantity', label: 'Quantity' },
  { key: 'reserved_quantity', label: 'Reserved' },
  { key: 'available_quantity', label: 'Available' },
  { key: 'reorder_point', label: 'Reorder point' },
]
const stockLevels = ref<Record<string, unknown>[]>([])
const warehouses = ref<Record<string, unknown>[]>([])
const skus = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({ warehouse_id: '', sku_id: '', quantity: '', reorder_point: '' })
const stockDisplay = computed(() => {
  const wMap: Record<string, string> = {}
  warehouses.value.forEach((w: Record<string, unknown>) => { wMap[w.id as string] = (w.name as string) || w.id as string })
  const sMap: Record<string, string> = {}
  skus.value.forEach((s: Record<string, unknown>) => { sMap[s.id as string] = (s.name as string) || s.id as string })
  return stockLevels.value.map((row: Record<string, unknown>) => ({
    ...row,
    warehouse_name: wMap[row.warehouse_id as string] || row.warehouse_id,
    sku_name: sMap[row.sku_id as string] || row.sku_id,
  }))
})
const filteredStock = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return stockDisplay.value
  return stockDisplay.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.warehouse_name, r.sku_name, r.quantity, r.reorder_point].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredStock.value.length / pageSize)))
const paginatedStock = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredStock.value.slice(start, start + pageSize)
})

async function fetchStock() {
  loading.value = true
  const res = await api<unknown[]>('/api/inventory/stock')
  if (res.status === 'success' && Array.isArray(res.data)) stockLevels.value = res.data as Record<string, unknown>[]
  loading.value = false
}

async function fetchWarehouses() {
  const res = await api<unknown[]>('/api/inventory/warehouses')
  if (res.status === 'success' && Array.isArray(res.data)) warehouses.value = res.data as Record<string, unknown>[]
}

async function fetchSkus() {
  const res = await api<unknown[]>('/api/inventory/skus')
  if (res.status === 'success' && Array.isArray(res.data)) skus.value = res.data as Record<string, unknown>[]
}

function openForm() {
  form.warehouse_id = ''
  form.sku_id = ''
  form.quantity = ''
  form.reorder_point = ''
  modalOpen.value = true
}

async function saveStock() {
  if (!form.warehouse_id || !form.sku_id) return
  saving.value = true
  const res = await api('/api/inventory/stock', {
    method: 'POST',
    body: JSON.stringify({
      warehouse_id: form.warehouse_id,
      sku_id: form.sku_id,
      quantity: Number(form.quantity) || 0,
      reorder_point: form.reorder_point ? Number(form.reorder_point) : undefined,
    }),
  })
  if (res.status === 'success') { modalOpen.value = false; await fetchStock() }
  saving.value = false
}

onMounted(() => { fetchStock(); fetchWarehouses(); fetchSkus() })
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
