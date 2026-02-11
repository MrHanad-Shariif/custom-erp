<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Leads'" />
    <div class="space-y-5">
      <ComponentCard title="Leads">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <input v-model="searchQuery" type="search" placeholder="Search leads..." class="search-input" />
          <button type="button" @click="openForm()" class="inline-flex items-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Add Lead
          </button>
        </div>
        <ErpDataTable :columns="columns" :data="paginatedLeads" :loading="loading" empty-text="No leads yet. Click Add Lead to create one." :show-actions="true" :on-edit="openForm" :on-delete="confirmDelete" />
        <ErpPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" :total="filteredLeads.length" :page-size="pageSize" @update:page="page = $event" />
      </ComponentCard>
    </div>
    <ErpFormModal
      :open="modalOpen"
      :title="editingId ? 'Edit Lead' : 'Add Lead'"
      :submit-label="editingId ? 'Update' : 'Create'"
      :saving="saving"
      @close="modalOpen = false"
      @submit="saveLead"
    >
      <ErpFormField v-model="form.company_name" label="Company name" required />
      <ErpFormField v-model="form.contact_name" label="Contact name" />
      <ErpFormField v-model="form.email" label="Email" type="email" />
      <ErpFormField v-model="form.phone" label="Phone" />
      <div>
        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Status</label>
        <select v-model="form.status" class="input-erp">
          <option value="prospect">Prospect</option>
          <option value="qualified">Qualified</option>
          <option value="proposal">Proposal</option>
          <option value="negotiation">Negotiation</option>
          <option value="closed_won">Closed Won</option>
          <option value="closed_lost">Closed Lost</option>
        </select>
      </div>
      <ErpFormField v-model="form.value" label="Value" type="number" placeholder="0" />
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
  { key: 'company_name', label: 'Company' },
  { key: 'contact_name', label: 'Contact' },
  { key: 'email', label: 'Email' },
  { key: 'status', label: 'Status', type: 'badge' },
  { key: 'value', label: 'Value' },
]
const leads = ref<Record<string, unknown>[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const searchQuery = ref('')
const page = ref(1)
const pageSize = 10
const filteredLeads = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return leads.value
  return leads.value.filter((row) => {
    const r = row as Record<string, unknown>
    return [r.company_name, r.contact_name, r.email, r.status, r.value].some((v) => String(v ?? '').toLowerCase().includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredLeads.value.length / pageSize)))
const paginatedLeads = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredLeads.value.slice(start, start + pageSize)
})
const form = reactive({
  company_name: '',
  contact_name: '',
  email: '',
  phone: '',
  status: 'prospect',
  value: '0',
})

async function fetchLeads() {
  loading.value = true
  const res = await api<unknown[]>('/api/crm/leads')
  if (res.status === 'success' && Array.isArray(res.data)) leads.value = res.data as Record<string, unknown>[]
  loading.value = false
}

function openForm(row?: Record<string, unknown>) {
  editingId.value = row ? (row.id as string) : null
  if (row) {
    form.company_name = String(row.company_name ?? '')
    form.contact_name = String(row.contact_name ?? '')
    form.email = String(row.email ?? '')
    form.phone = String(row.phone ?? '')
    form.status = String(row.status ?? 'prospect')
    form.value = String(row.value ?? '0')
  } else {
    form.company_name = ''
    form.contact_name = ''
    form.email = ''
    form.phone = ''
    form.status = 'prospect'
    form.value = '0'
  }
  modalOpen.value = true
}

async function saveLead() {
  if (!form.company_name.trim()) return
  saving.value = true
  const payload = {
    company_name: form.company_name.trim(),
    contact_name: form.contact_name.trim(),
    email: form.email.trim(),
    phone: form.phone.trim(),
    status: form.status,
    value: Number(form.value) || 0,
  }
  if (editingId.value) {
    const res = await api(`/api/crm/leads/${editingId.value}`, { method: 'PUT', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchLeads() }
  } else {
    const res = await api('/api/crm/leads', { method: 'POST', body: JSON.stringify(payload) })
    if (res.status === 'success') { modalOpen.value = false; await fetchLeads() }
  }
  saving.value = false
}

function confirmDelete(row: Record<string, unknown>) {
  if (window.confirm('Delete this lead?')) {
    // Backend may not have delete; skip or add endpoint
    fetchLeads()
  }
}

onMounted(fetchLeads)
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
