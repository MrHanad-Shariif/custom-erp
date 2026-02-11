<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Dashboard'" />
    <div class="space-y-6">
      <!-- Overview cards -->
      <div>
        <h2 class="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">Overview</h2>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <DashboardCard
            v-for="card in overviewCards"
            :key="card.key"
            :label="card.label"
            :value="card.loading ? '—' : String(card.value)"
            :icon="card.icon"
            :to="card.to"
          />
        </div>
      </div>

      <!-- Charts row -->
      <div class="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <!-- Leads by status -->
        <ComponentCard title="Leads by status" desc="Distribution of leads by pipeline stage">
          <div v-if="loadingCharts" class="flex items-center justify-center py-12 text-gray-500">Loading...</div>
          <div v-else-if="leadsDonutSeries.length === 0" class="py-12 text-center text-gray-500 dark:text-gray-400">No leads yet</div>
          <div v-else class="min-h-[280px]">
            <VueApexCharts type="donut" height="280" :options="leadsChartOptions" :series="leadsDonutSeries" />
          </div>
        </ComponentCard>

        <!-- Stock by warehouse -->
        <ComponentCard title="Stock by warehouse" desc="Total quantity per warehouse">
          <div v-if="loadingCharts" class="flex items-center justify-center py-12 text-gray-500">Loading...</div>
          <div v-else-if="stockCategories.length === 0" class="py-12 text-center text-gray-500 dark:text-gray-400">No stock data yet</div>
          <div v-else class="min-h-[280px] -ml-2">
            <VueApexCharts type="bar" height="280" :options="stockChartOptions" :series="stockSeries" />
          </div>
        </ComponentCard>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import ComponentCard from '@/components/common/ComponentCard.vue'
import DashboardCard from '@/components/dashboard/DashboardCard.vue'
import VueApexCharts from 'vue3-apexcharts'
import { api } from '@/api/client'

interface DashboardData {
  customers_count: number
  employees_count: number
  purchase_orders_count: number
  projects_count: number
  invoices_count: number
  leads_count: number
  leads_by_status: { status: string; count: number }[]
  stock_by_warehouse: { warehouse_name: string; total_quantity: number }[]
}

const data = ref<DashboardData | null>(null)
const loading = ref(true)
const loadingCharts = ref(true)

const overviewCards = computed(() => [
  { key: 'customers', label: 'Customers', value: data.value?.customers_count ?? 0, icon: 'users', to: '/crm/customers', loading: loading.value },
  { key: 'employees', label: 'Employees', value: data.value?.employees_count ?? 0, icon: 'briefcase', to: '/hrm/employees', loading: loading.value },
  { key: 'purchase_orders', label: 'Purchase orders', value: data.value?.purchase_orders_count ?? 0, icon: 'truck', to: '/inventory/purchase-orders', loading: loading.value },
  { key: 'projects', label: 'Projects', value: data.value?.projects_count ?? 0, icon: 'folder', to: '/pm/projects', loading: loading.value },
  { key: 'invoices', label: 'Invoices', value: data.value?.invoices_count ?? 0, icon: 'file-text', to: '/finance/invoices', loading: loading.value },
  { key: 'leads', label: 'Leads', value: data.value?.leads_count ?? 0, icon: 'target', to: '/crm/leads', loading: loading.value },
])

const leadsDonutSeries = computed(() =>
  (data.value?.leads_by_status ?? []).map((x) => x.count)
)

const leadsChartOptions = computed(() => {
  const list = data.value?.leads_by_status ?? []
  const labels = list.map((x) => formatStatus(x.status))
  return {
    chart: { type: 'donut', fontFamily: 'Outfit, sans-serif' },
    labels,
    colors: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#6b7280'],
    legend: { position: 'bottom', horizontalAlign: 'center' },
    dataLabels: { enabled: true },
    plotOptions: { pie: { donut: { size: '65%' } } },
  }
})

function formatStatus(s: string): string {
  return s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

const stockCategories = computed(() => data.value?.stock_by_warehouse?.map((x) => x.warehouse_name) ?? [])
const stockSeries = computed(() => [
  {
    name: 'Quantity',
    data: data.value?.stock_by_warehouse?.map((x) => x.total_quantity) ?? [],
  },
])

const stockChartOptions = computed(() => ({
  chart: {
    type: 'bar',
    fontFamily: 'Outfit, sans-serif',
    toolbar: { show: false },
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '55%',
      borderRadius: 4,
      borderRadiusApplication: 'end',
    },
  },
  colors: ['#3b82f6'],
  dataLabels: { enabled: false },
  stroke: { show: true, width: 2, colors: ['transparent'] },
  xaxis: {
    categories: stockCategories.value,
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: { title: { text: 'Quantity' } },
  grid: {
    yaxis: { lines: { show: true } },
    xaxis: { lines: { show: false } },
  },
  fill: { opacity: 1 },
  tooltip: {
    y: { formatter: (val: number) => String(val) },
  },
}))

async function fetchDashboard() {
  loading.value = true
  loadingCharts.value = true
  const res = await api<DashboardData>('/api/dashboard')
  if (res.status === 'success' && res.data) {
    data.value = res.data
  }
  loading.value = false
  loadingCharts.value = false
}

onMounted(fetchDashboard)
</script>
