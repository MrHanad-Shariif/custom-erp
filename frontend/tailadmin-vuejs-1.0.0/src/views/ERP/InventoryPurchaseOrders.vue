<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Purchase Orders'" />
    <div class="space-y-5">
      <ComponentCard title="Purchase Orders">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Search purchase orders..."
            class="search-input"
          />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Create PO
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedPos" :loading="loading" empty-text="No purchase orders yet." :show-actions="false" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredPos.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="'Create purchase order'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="savePo">
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Warehouse *</label>
        <select v-model="form.warehouse_id" class="input-erp" required>
          <option value="">Select warehouse</option>
          <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ (w as Record<string, unknown>).name }} ({{ (w as Record<string, unknown>).code }})</option>
        </select>
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Order date</label>
        <input v-model="form.order_date" type="date" class="input-erp date-input" />
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Expected date</label>
        <input v-model="form.expected_date" type="date" class="input-erp date-input" />
      </div>
      <p class="text-sm text-gray-500">After creating the PO you can add lines via the API. This form creates the header only.</p>
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
import ErpPagination from '@/components/erp/ErpPagination.vue'
import { api } from '@/api/client'

const columns = [
  { key: 'number', label: 'Number' },
  { key: 'warehouse_name', label: 'Warehouse' },
  { key: 'status', label: 'Status', type: 'badge' },
  { key: 'order_date', label: 'Order date' },
  { key: 'expected_date', label: 'Expected date' },
]
const purchaseOrders = ref<Record<string, unknown>[]>([])
const warehouses = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({ warehouse_id: '', order_date: '', expected_date: '' })

function warehouseName(id: unknown): string {
  if (!id) return '—'
  const w = warehouses.value.find((x) => (x as Record<string, unknown>).id === id) as Record<string, unknown> | undefined
  return (w?.name ?? w?.code ?? id) as string
}

const displayPos = computed(() =>
  purchaseOrders.value.map((po) => ({
    ...po,
    warehouse_name: warehouseName((po as Record<string, unknown>).warehouse_id),
  }))
)
const filteredPos = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return displayPos.value
  return displayPos.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.number, r.warehouse_name, r.status].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredPos.value.length / pageSize)))
const paginatedPos = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredPos.value.slice(start, start + pageSize)
})

async function fetchPos() {
  loading.value = true
  const res = await api<unknown[]>('/api/inventory/purchase-orders')
  if (res.status === 'success' && Array.isArray(res.data)) purchaseOrders.value = res.data as Record<string, unknown>[]
  loading.value = false
}

async function fetchWarehouses() {
  const res = await api<unknown[]>('/api/inventory/warehouses')
  if (res.status === 'success' && Array.isArray(res.data)) warehouses.value = res.data as Record<string, unknown>[]
}

function openForm() {
  form.warehouse_id = ''
  form.order_date = ''
  form.expected_date = ''
  modalOpen.value = true
}

async function savePo() {
  if (!form.warehouse_id) return
  saving.value = true
  const res = await api('/api/inventory/purchase-orders', {
    method: 'POST',
    body: JSON.stringify({
      warehouse_id: form.warehouse_id,
      order_date: form.order_date || undefined,
      expected_date: form.expected_date || undefined,
      lines: [],
    }),
  })
  if (res.status === 'success') { modalOpen.value = false; await fetchPos() }
  saving.value = false
}

onMounted(() => { fetchPos(); fetchWarehouses() })
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
  cursor: text;
}
.date-input { cursor: pointer; }
:deep(.dark) .input-erp,
:deep(.dark) .date-input,
:deep(.dark) .search-input {
  border-color: #374151;
  background: #111827;
  color: rgb(255 255 255 / 0.9);
}
</style>
