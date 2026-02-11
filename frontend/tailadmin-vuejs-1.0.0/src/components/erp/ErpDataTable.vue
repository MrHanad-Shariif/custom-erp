<template>
  <div class="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
    <div class="max-w-full overflow-x-auto custom-scrollbar">
      <table class="min-w-full">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700">
            <th v-for="col in columns" :key="col.key" class="px-4 py-3 text-left sm:px-5">
              <p class="font-medium text-gray-500 text-theme-xs dark:text-gray-400">{{ col.label }}</p>
            </th>
            <th v-if="showActions" class="px-4 py-3 text-right sm:px-5 w-28">
              <p class="font-medium text-gray-500 text-theme-xs dark:text-gray-400">Actions</p>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="(row, index) in data"
            :key="row.id || index"
            class="border-t border-gray-100 dark:border-gray-800"
          >
            <td v-for="col in columns" :key="col.key" class="px-4 py-3 sm:px-5">
              <router-link
                v-if="col.type === 'link' && col.toTemplate"
                :to="col.toTemplate.replace(/:id/g, String(row.id || ''))"
                class="text-brand-500 hover:underline text-theme-sm"
              >
                {{ col.linkLabel || 'View' }}
              </router-link>
              <span v-else-if="col.type === 'badge'" :class="badgeClass(getVal(row, col.key))">
                {{ getVal(row, col.key) || '—' }}
              </span>
              <span v-else class="text-gray-700 text-theme-sm dark:text-gray-300">
                {{ formatVal(getVal(row, col.key), col) }}
              </span>
            </td>
            <td v-if="showActions" class="px-4 py-3 text-right sm:px-5">
              <button
                v-if="onEdit"
                @click="onEdit(row)"
                class="mr-2 text-brand-500 hover:text-brand-600 text-sm font-medium"
              >
                Edit
              </button>
              <button
                v-if="onDelete"
                @click="onDelete(row)"
                class="text-red-500 hover:text-red-600 text-sm font-medium"
              >
                Delete
              </button>
            </td>
          </tr>
          <tr v-if="!loading && (!data || data.length === 0)">
            <td :colspan="columns.length + (showActions ? 1 : 0)" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
              {{ emptyText }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="loading" class="p-6 text-center text-gray-500">Loading...</div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    columns: { key: string; label: string; type?: string; toTemplate?: string; linkLabel?: string }[]
    data: Record<string, unknown>[]
    loading?: boolean
    emptyText?: string
    showActions?: boolean
    onEdit?: (row: Record<string, unknown>) => void
    onDelete?: (row: Record<string, unknown>) => void
  }>(),
  { loading: false, emptyText: 'No data yet.', showActions: true }
)

function getVal(row: Record<string, unknown>, key: string) {
  const parts = key.split('.')
  let v: unknown = row
  for (const p of parts) v = (v as Record<string, unknown>)?.[p]
  return v
}

function formatVal(v: unknown, col: { key: string; label: string; type?: string }): string {
  if (v == null) return '—'
  if (col.key.includes('date') || col.key.includes('_at')) return String(v).slice(0, 10)
  if (typeof v === 'number') return String(v)
  return String(v)
}

function badgeClass(status: unknown) {
  const s = String(status || '').toLowerCase()
  if (s === 'true' || s === 'active' || s === 'approved' || s === 'paid' || s === 'closed_won')
    return 'rounded-full px-2 py-0.5 text-theme-xs font-medium bg-success-50 text-success-700 dark:bg-success-500/15 dark:text-success-500'
  if (s === 'draft' || s === 'pending' || s === 'prospect')
    return 'rounded-full px-2 py-0.5 text-theme-xs font-medium bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-warning-400'
  if (s === 'closed_lost' || s === 'cancelled')
    return 'rounded-full px-2 py-0.5 text-theme-xs font-medium bg-error-50 text-error-700 dark:bg-error-500/15 dark:text-error-500'
  return 'rounded-full px-2 py-0.5 text-theme-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-500/15 dark:text-gray-400'
}
</script>
