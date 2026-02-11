<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="project?.name || 'Project'" />
    <ComponentCard v-if="project" :title="project.name">
      <p>Code: {{ project.code }}, Status: {{ project.status }}</p>
    </ComponentCard>
    <p v-if="loading" class="p-4">Loading...</p>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import ComponentCard from '@/components/common/ComponentCard.vue'
import { api } from '@/api/client'

const route = useRoute()
const project = ref<{ name: string; code: string; status: string } | null>(null)
const loading = ref(true)
onMounted(async () => {
  const res = await api<{ name: string; code: string; status: string }>(`/api/pm/projects/${route.params.id}`)
  if (res.status === 'success') project.value = res.data
  loading.value = false
})
</script>
