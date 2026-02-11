<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Payroll'" />
    <div class="space-y-5">
      <ComponentCard title="Payroll runs">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search payroll..." class="search-input" />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Create payroll run
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedRuns" :loading="loading" empty-text="No payroll runs yet." :show-actions="false" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredRuns.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="'Create payroll run'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveRun">
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Period start *</label>
        <input v-model="form.period_start" type="date" class="input-erp date-input" required />
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Period end *</label>
        <input v-model="form.period_end" type="date" class="input-erp date-input" required />
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
import ErpPagination from '@/components/erp/ErpPagination.vue'
import { api } from '@/api/client'

const columns = [
  { key: 'period', label: 'Period' },
  { key: 'period_start', label: 'Start' },
  { key: 'period_end', label: 'End' },
  { key: 'status', label: 'Status', type: 'badge' },
]
const runs = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({ period_start: '', period_end: '' })
const filteredRuns = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return runs.value
  return runs.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.period, r.period_start, r.period_end, r.status].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredRuns.value.length / pageSize)))
const paginatedRuns = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredRuns.value.slice(start, start + pageSize)
})

async function fetchRuns() {
  loading.value = true
  const res = await api<unknown[]>('/api/hrm/payroll')
  if (res.status === 'success' && Array.isArray(res.data)) runs.value = res.data as Record<string, unknown>[]
  loading.value = false
}

function openForm() {
  form.period_start = ''
  form.period_end = ''
  modalOpen.value = true
}

async function saveRun() {
  if (!form.period_start || !form.period_end) return
  saving.value = true
  const res = await api('/api/hrm/payroll', {
    method: 'POST',
    body: JSON.stringify({ period_start: form.period_start, period_end: form.period_end }),
  })
  if (res.status === 'success') { modalOpen.value = false; await fetchRuns() }
  saving.value = false
}

onMounted(fetchRuns)
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
