<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Employees'" />
    <div class="space-y-5">
      <ComponentCard title="Employees">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search employees..." class="search-input" />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Add Employee
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedEmployees" :loading="loading" empty-text="No employees yet." :on-edit="openForm" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredEmployees.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal :open="modalOpen" :title="editingId ? 'Edit Employee' : 'Add Employee'" :saving="saving" submit-label="Save" @close="modalOpen = false" @submit="saveEmployee">
      <ErpFormField v-model="form.full_name" label="Full name" required />
      <ErpFormField v-model="form.employee_code" label="Employee code" placeholder="Auto if empty" />
      <ErpFormField v-model="form.job_title" label="Job title" />
      <ErpFormField v-model="form.department" label="Department" />
      <ErpFormField v-model="form.base_salary_monthly" label="Base salary (monthly)" type="number" />
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Hire date</label>
        <input v-model="form.hire_date" type="date" class="input-erp date-input" />
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
  { key: 'employee_code', label: 'Code' },
  { key: 'full_name', label: 'Name' },
  { key: 'job_title', label: 'Job title' },
  { key: 'department', label: 'Department' },
  { key: 'base_salary_monthly', label: 'Base salary' },
  { key: 'is_active', label: 'Active', type: 'badge' },
]
const employees = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const filteredEmployees = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return employees.value
  return employees.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.employee_code, r.full_name, r.job_title, r.department].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredEmployees.value.length / pageSize)))
const paginatedEmployees = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredEmployees.value.slice(start, start + pageSize)
})
const form = reactive({
  full_name: '',
  employee_code: '',
  job_title: '',
  department: '',
  base_salary_monthly: '',
  hire_date: '',
})

async function fetchEmployees() {
  loading.value = true
  const res = await api<unknown[]>('/api/hrm/employees')
  if (res.status === 'success' && Array.isArray(res.data)) employees.value = res.data as Record<string, unknown>[]
  loading.value = false
}

function openForm(row?: Record<string, unknown>) {
  editingId.value = row ? (row.id as string) : null
  if (row) {
    form.full_name = String(row.full_name ?? '')
    form.employee_code = String(row.employee_code ?? '')
    form.job_title = String(row.job_title ?? '')
    form.department = String(row.department ?? '')
    form.base_salary_monthly = String(row.base_salary_monthly ?? '')
    form.hire_date = row.hire_date ? String(row.hire_date).slice(0, 10) : ''
  } else {
    form.full_name = ''
    form.employee_code = ''
    form.job_title = ''
    form.department = ''
    form.base_salary_monthly = ''
    form.hire_date = ''
  }
  modalOpen.value = true
}

async function saveEmployee() {
  if (!form.full_name.trim()) return
  saving.value = true
  const payload = {
    full_name: form.full_name.trim(),
    employee_code: form.employee_code.trim() || undefined,
    job_title: form.job_title.trim(),
    department: form.department.trim(),
    base_salary_monthly: form.base_salary_monthly ? Number(form.base_salary_monthly) : undefined,
    hire_date: form.hire_date || undefined,
  }
  if (editingId.value) {
    const res = await api(`/api/hrm/employees/${editingId.value}`, { method: 'PUT', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchEmployees() }
  } else {
    const res = await api('/api/hrm/employees', { method: 'POST', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchEmployees() }
  }
  saving.value = false
}

onMounted(fetchEmployees)
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
