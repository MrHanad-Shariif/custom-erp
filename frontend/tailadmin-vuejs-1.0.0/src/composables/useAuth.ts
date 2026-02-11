import { ref, computed } from 'vue'
import { auth as authApi } from '@/api/client'

const STORAGE_TOKEN = 'erp_access_token'
const STORAGE_REFRESH = 'erp_refresh_token'

export interface User {
  id: string
  organization_id: string
  email: string
  full_name: string
  is_active: boolean
}

export interface Organization {
  id: string
  name: string
  code: string
  timezone: string
}

const user = ref<User | null>(null)
const organization = ref<Organization | null>(null)
const permissions = ref<string[]>([])
const initialized = ref(false)

export function useAuth() {
  const accessToken = computed(() => localStorage.getItem(STORAGE_TOKEN))
  const isAuthenticated = computed(() => !!accessToken.value)

  function setSession(
    access: string,
    refresh: string | null,
    u: User | null,
    org: Organization | null,
    perms: string[]
  ) {
    if (access) localStorage.setItem(STORAGE_TOKEN, access)
    else localStorage.removeItem(STORAGE_TOKEN)
    if (refresh) localStorage.setItem(STORAGE_REFRESH, refresh)
    else localStorage.removeItem(STORAGE_REFRESH)
    user.value = u
    organization.value = org
    permissions.value = perms
  }

  function clearSession() {
    localStorage.removeItem(STORAGE_TOKEN)
    localStorage.removeItem(STORAGE_REFRESH)
    user.value = null
    organization.value = null
    permissions.value = []
  }

  function hasPermission(permissionId: string): boolean {
    return permissions.value.includes(permissionId)
  }

  function hasAnyPermission(...ids: string[]): boolean {
    return ids.some((id) => permissions.value.includes(id))
  }

  async function login(email: string, password: string) {
    const res = await authApi.login(email, password)
    if (res.status !== 'success' || !res.data.access_token) {
      throw new Error(res.message || 'Login failed')
    }
    const d = res.data as {
      user: User
      organization: Organization
      access_token: string
      refresh_token: string
    }
    setSession(d.access_token, d.refresh_token, d.user, d.organization, [])
    await fetchMe()
    return res
  }

  async function fetchMe() {
    const res = await authApi.me()
    if (res.status !== 'success' || !res.data) {
      clearSession()
      return
    }
    const d = res.data as { user: User; organization: Organization; permissions: string[] }
    user.value = d.user as User
    organization.value = d.organization as Organization
    permissions.value = d.permissions || []
    initialized.value = true
  }

  async function initFromStorage() {
    if (initialized.value) return
    if (!localStorage.getItem(STORAGE_TOKEN)) {
      initialized.value = true
      return
    }
    await fetchMe()
  }

  function logout() {
    clearSession()
    initialized.value = false
  }

  return {
    user,
    organization,
    permissions,
    accessToken,
    isAuthenticated,
    initialized,
    setSession,
    clearSession,
    hasPermission,
    hasAnyPermission,
    login,
    fetchMe,
    initFromStorage,
    logout,
  }
}
