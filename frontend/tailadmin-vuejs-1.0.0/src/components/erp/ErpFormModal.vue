<template>
  <div v-if="open" class="fixed inset-0 z-99999 flex items-center justify-center overflow-y-auto p-4">
    <div class="fixed inset-0 bg-gray-600/50 dark:bg-gray-900/70" @click="$emit('close')"></div>
    <div class="relative z-10 w-full max-w-lg rounded-xl border border-gray-200 bg-white p-6 shadow-xl dark:border-gray-800 dark:bg-gray-900 overflow-visible">
      <h3 class="mb-4 text-lg font-semibold text-gray-800 dark:text-white">{{ title }}</h3>
      <form @submit.prevent="$emit('submit')" class="space-y-4">
        <slot></slot>
        <div class="flex justify-end gap-3 pt-4">
          <button type="button" @click="$emit('close')"
            class="erp-modal-cancel">
            Cancel
          </button>
          <button type="submit" :disabled="saving" class="erp-modal-save">
            {{ saving ? 'Saving...' : submitLabel }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    open: boolean
    title: string
    submitLabel?: string
    saving?: boolean
  }>(),
  { submitLabel: 'Save', saving: false }
)
defineEmits<{ close: []; submit: [] }>()
</script>

<style scoped>
.erp-modal-cancel {
  min-width: 5rem;
  padding: 0.625rem 1.25rem;
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  background: #f3f4f6;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}
.erp-modal-cancel:hover { background: #e5e7eb; }
.erp-modal-save {
  min-width: 5.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background: #3b82f6;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}
.erp-modal-save:hover:not(:disabled) { background: #2563eb; }
.erp-modal-save:disabled { opacity: 0.6; cursor: not-allowed; }
:deep(.dark) .erp-modal-cancel {
  background: #374151;
  color: #e5e7eb;
}
:deep(.dark) .erp-modal-cancel:hover { background: #4b5563; }
</style>
