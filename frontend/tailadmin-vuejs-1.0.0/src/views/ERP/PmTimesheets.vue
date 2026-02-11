<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Timesheets'" />
    <div class="space-y-5">
      <ComponentCard title="Timesheets">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search timesheets..." class="search-input" />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Log time
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedTimesheets" :loading="loading" empty-text="No timesheets yet." :show-actions="false" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredTimesheets.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="'Log time'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveTimesheet">
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Employee *</label>
        <select v-model="form.employee_id" class="input-erp" required>
          <option value="">Select employee</option>
          <option v-for="e in employees" :key="e.id" :value="e.id">{{ (e as Record<string, unknown>).full_name }} ({{ (e as Record<string, unknown>).employee_code }})</option>
        </select>
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Task *</label>
        <select v-model="form.task_id" class="input-erp" required>
          <option value="">Select task</option>
          <option v-for="t in tasks" :key="t.id" :value="t.id">{{ (t as Record<string, unknown>).name }}</option>
        </select>
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Work date *</label>
        <input v-model="form.work_date" type="date" class="input-erp date-input" required />
      </div>
      <ErpFormField v-model="form.hours" label="Hours" type="number" required />
      <ErpFormField v-model="form.notes" label="Notes" type="textarea" />
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
  { key: 'work_date', label: 'Date' },
  { key: 'employee_name', label: 'Employee' },
  { key: 'task_name', label: 'Task' },
  { key: 'hours', label: 'Hours' },
  { key: 'status', label: 'Status', type: 'badge' },
]
const timesheets = ref<Record<string, unknown>[]>([])
const employees = ref<Record<string, unknown>[]>([])
const tasks = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const form = reactive({ employee_id: '', task_id: '', work_date: '', hours: '', notes: '' })

function employeeName(id: unknown): string {
  if (!id) return '—'
  const e = employees.value.find((x) => (x as Record<string, unknown>).id === id) as Record<string, unknown> | undefined
  return (e?.full_name ?? e?.employee_code ?? id) as string
}
function taskName(id: unknown): string {
  if (!id) return '—'
  const t = tasks.value.find((x) => (x as Record<string, unknown>).id === id) as Record<string, unknown> | undefined
  return (t?.name ?? id) as string
}

const displayTimesheets = computed(() =>
  timesheets.value.map((ts) => ({
    ...ts,
    employee_name: employeeName((ts as Record<string, unknown>).employee_id),
    task_name: taskName((ts as Record<string, unknown>).task_id),
  }))
)
const filteredTimesheets = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return displayTimesheets.value
  return displayTimesheets.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.work_date, r.employee_name, r.task_name, r.hours, r.status].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredTimesheets.value.length / pageSize)))
const paginatedTimesheets = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredTimesheets.value.slice(start, start + pageSize)
})

async function fetchTimesheets() {
  loading.value = true
  const res = await api<unknown[]>('/api/pm/timesheets')
  if (res.status === 'success' && Array.isArray(res.data)) timesheets.value = res.data as Record<string, unknown>[]
  loading.value = false
}

async function fetchEmployees() {
  const res = await api<unknown[]>('/api/hrm/employees')
  if (res.status === 'success' && Array.isArray(res.data)) employees.value = res.data as Record<string, unknown>[]
}

async function fetchTasks() {
  const projRes = await api<unknown[]>('/api/pm/projects')
  if (projRes.status !== 'success' || !Array.isArray(projRes.data)) return
  const all: Record<string, unknown>[] = []
  for (const p of projRes.data as Record<string, unknown>[]) {
    const r = await api<{ milestones?: { tasks?: Record<string, unknown>[] }[] }>(`/api/pm/projects/${p.id}`)
    if (r.status === 'success' && r.data.milestones)
      r.data.milestones.forEach((m: { tasks?: Record<string, unknown>[] }) => m.tasks?.forEach((t: Record<string, unknown>) => all.push({ ...t, name: `${t.name} (${p.name})` })))
  }
  tasks.value = all
}

function openForm() {
  form.employee_id = ''
  form.task_id = ''
  form.work_date = ''
  form.hours = ''
  form.notes = ''
  modalOpen.value = true
}

async function saveTimesheet() {
  if (!form.employee_id || !form.task_id || !form.work_date) return
  saving.value = true
  const res = await api('/api/pm/timesheets', {
    method: 'POST',
    body: JSON.stringify({
      employee_id: form.employee_id,
      task_id: form.task_id,
      work_date: form.work_date,
      hours: Number(form.hours) || 0,
      notes: form.notes.trim(),
    }),
  })
  if (res.status === 'success') { modalOpen.value = false; await fetchTimesheets() }
  saving.value = false
}

onMounted(() => { fetchTimesheets(); fetchEmployees(); fetchTasks() })
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
