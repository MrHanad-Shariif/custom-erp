<template>
  <router-link
    v-if="to"
    :to="to"
    class="dashboard-card block rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md dark:border-gray-800 dark:bg-white/[0.03] dark:hover:bg-white/[0.06]"
  >
    <div class="flex items-start justify-between">
      <div class="flex h-11 w-11 items-center justify-center rounded-lg bg-brand-500/10 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400">
        <component :is="iconComponent" class="h-6 w-6" />
      </div>
      <ChevronRightIcon v-if="to" class="h-5 w-5 text-gray-400 dark:text-gray-500" />
    </div>
    <p class="mt-4 text-sm font-medium text-gray-500 dark:text-gray-400">{{ label }}</p>
    <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">{{ value }}</p>
  </router-link>
  <div
    v-else
    class="dashboard-card rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-white/[0.03]"
  >
    <div class="flex h-11 w-11 items-center justify-center rounded-lg bg-brand-500/10 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400">
      <component :is="iconComponent" class="h-6 w-6" />
    </div>
    <p class="mt-4 text-sm font-medium text-gray-500 dark:text-gray-400">{{ label }}</p>
    <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">{{ value }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  UserGroupIcon,
  FolderIcon,
  BoxCubeIcon,
  TaskIcon,
  DocsIcon,
  FlagIcon,
  ChevronRightIcon,
} from '@/icons'

const props = withDefaults(
  defineProps<{
    label: string
    value: string
    icon?: string
    to?: string
  }>(),
  { icon: 'users' }
)

const iconComponent = computed(() => {
  const map: Record<string, unknown> = {
    users: UserGroupIcon,
    briefcase: TaskIcon,
    truck: BoxCubeIcon,
    folder: FolderIcon,
    'file-text': DocsIcon,
    target: FlagIcon,
  }
  return (map[props.icon] ?? UserGroupIcon) as object
})
</script>
