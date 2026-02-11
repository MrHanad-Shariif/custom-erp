<template>
  <FullScreenLayout>
    <div class="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-gray-900">
      <div v-if="errorCode" class="max-w-md p-6 text-center">
        <p class="mb-4 text-sm text-red-500 dark:text-red-400">{{ errorMessage || 'Sign-in failed.' }}</p>
        <router-link
          to="/signin"
          class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white rounded-lg bg-brand-500 hover:bg-brand-600"
        >
          Back to Sign In
        </router-link>
      </div>
      <div v-else class="text-center">
        <p class="text-sm text-gray-600 dark:text-gray-400">Signing you in...</p>
      </div>
    </div>
  </FullScreenLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FullScreenLayout from '@/components/layout/FullScreenLayout.vue'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { setSession, fetchMe } = useAuth()
const errorCode = ref('')
const errorMessage = ref('')

onMounted(async () => {
  const hash = window.location.hash?.slice(1) || ''
  const params = new URLSearchParams(hash || window.location.search)

  const err = params.get('error')
  const msg = params.get('message')
  if (err || msg) {
    errorCode.value = err || 'error'
    errorMessage.value = msg || 'Something went wrong.'
    return
  }

  const access_token = params.get('access_token')
  const refresh_token = params.get('refresh_token')
  if (access_token) {
    setSession(access_token, refresh_token, null, null, [])
    await fetchMe()
    router.replace('/')
    return
  }

  errorCode.value = 'missing_tokens'
  errorMessage.value = 'No tokens received. Please try again.'
})
</script>
