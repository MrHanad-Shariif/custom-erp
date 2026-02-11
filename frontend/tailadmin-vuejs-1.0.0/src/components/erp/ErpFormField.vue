<template>
  <div>
    <label v-if="label" class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
      {{ label }}<span v-if="required" class="text-red-500">*</span>
    </label>
    <input
      v-if="type !== 'textarea'"
      :type="type"
      :value="modelValue"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      :placeholder="placeholder"
      class="input-erp"
    />
    <textarea
      v-else
      :value="modelValue"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
      :placeholder="placeholder"
      rows="3"
      class="input-erp"
    ></textarea>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string
    type?: string
    modelValue?: string | number
    placeholder?: string
    required?: boolean
  }>(),
  { type: 'text' }
)
defineEmits<{ 'update:modelValue': [v: string | number] }>()
</script>

<style scoped>
.input-erp {
  height: 2.75rem;
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  background: transparent;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  color: #1f2937;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  outline: none;
}
.input-erp::placeholder {
  color: #9ca3af;
}
.input-erp:focus {
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1);
}
:deep(.dark) .input-erp {
  border-color: #374151;
  background: #111827;
  color: rgb(255 255 255 / 0.9);
}
:deep(.dark) .input-erp::placeholder {
  color: rgb(255 255 255 / 0.3);
}
:deep(.dark) .input-erp:focus {
  border-color: #1e3a5f;
}
</style>
