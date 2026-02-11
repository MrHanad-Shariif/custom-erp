/**
 * ERP API client. Uses fetch with JWT from localStorage.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

function getToken(): string | null {
  return localStorage.getItem('erp_access_token')
}

export interface ApiResponse<T = unknown> {
  status: 'success' | 'error'
  data: T
  message?: string
  errors?: Record<string, string[]>
}

export async function api<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const token = getToken()
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  const json = await res.json().catch(() => ({ status: 'error', data: {}, message: 'Invalid response' }))
  if (!res.ok) {
    return {
      status: 'error',
      data: json.data ?? {},
      message: json.message || `Request failed: ${res.status}`,
      errors: json.errors,
    }
  }
  return json as ApiResponse<T>
}

export const auth = {
  login: (email: string, password: string) =>
    api<{ user: unknown; organization: unknown; access_token: string; refresh_token: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (body: {
    organization_name: string
    organization_code: string
    email: string
    password: string
    full_name: string
  }) =>
    api<{ user: unknown; organization: unknown; access_token: string; refresh_token: string }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  me: () =>
    api<{ user: unknown; organization: unknown; permissions: string[] }>('/api/auth/me'),
  refresh: () =>
    api<{ access_token: string }>('/api/auth/refresh', { method: 'POST' }),
}
