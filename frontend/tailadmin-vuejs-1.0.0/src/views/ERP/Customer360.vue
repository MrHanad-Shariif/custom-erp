<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Customer 360'" />
    <div class="space-y-5" v-if="data">
      <ComponentCard :title="data.customer?.name || 'Customer'">
        <p class="text-gray-600 dark:text-gray-400">Code: {{ data.customer?.code }}</p>
      </ComponentCard>
      <ComponentCard title="Projects">
        <ul class="list-disc list-inside">
          <li v-for="p in data.projects" :key="p.id">{{ p.name }} ({{ p.status }})</li>
          <li v-if="!data.projects?.length">No projects.</li>
        </ul>
      </ComponentCard>
      <ComponentCard title="Unpaid Invoices">
        <ul class="list-disc list-inside">
          <li v-for="i in data.unpaid_invoices" :key="i.id">{{ i.number }} — {{ i.amount }}</li>
          <li v-if="!data.unpaid_invoices?.length">No unpaid invoices.</li>
        </ul>
      </ComponentCard>
    </div>
    <p v-if="loading" class="p-4">Loading...</p>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import ComponentCard from '@/components/common/ComponentCard.vue'
import { api } from '@/api/client'

const route = useRoute()
const data = ref<{
  customer?: { name: string; code: string }
  projects?: Array<{ id: string; name: string; status: string }>
  unpaid_invoices?: Array<{ id: string; number: string; amount: number }>
} | null>(null)
const loading = ref(true)

onMounted(async () => {
  const id = route.params.id as string
  const res = await api<typeof data.value>(`/api/crm/customers/${id}/360`)
  if (res.status === 'success') data.value = res.data as typeof data.value
  loading.value = false
})
</script>
