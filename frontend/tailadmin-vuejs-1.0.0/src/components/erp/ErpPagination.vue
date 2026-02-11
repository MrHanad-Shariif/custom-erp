<template>
  <div class="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-gray-200 pt-4 dark:border-gray-700">
    <p class="text-sm text-gray-600 dark:text-gray-400">
      Showing {{ ((currentPage - 1) * pageSize) + 1 }}–{{ Math.min(currentPage * pageSize, total) }} of {{ total }}
    </p>
    <div class="flex items-center gap-1">
      <button
        type="button"
        :disabled="currentPage <= 1"
        class="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
        @click="$emit('update:page', currentPage - 1)"
      >
        Previous
      </button>
      <span class="px-2 text-sm text-gray-600 dark:text-gray-400">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button
        type="button"
        :disabled="currentPage >= totalPages"
        class="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
        @click="$emit('update:page', currentPage + 1)"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  currentPage: number
  totalPages: number
  total: number
  pageSize: number
}>()
defineEmits<{ 'update:page': [page: number] }>()
</script>
