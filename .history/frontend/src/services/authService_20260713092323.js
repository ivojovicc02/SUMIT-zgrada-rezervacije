import { computed, ref } from 'vue'
import api from './api'

export const currentUser = ref(null)
export const initialized = ref(false)

export const isAuthenticated = computed(() =>
  Boolean(currentUser.value),
)

export const isAdmin = computed(() =>
  currentUser.value?.role?.toUpperCase() === 'ADMIN',
)

export async function login(email, password) {
  const response = await api.post('/auth/login', {
    email,
    password,
  })

  currentUser.value =
    response.data.user ?? response.data

  return currentUser.value
}

export async function fetchCurrentUser() {
  try {
    const response = await api.get('/auth/me')

    currentUser.value =
      response.data.user ?? response.data
  } catch {
    currentUser.value = null
  } finally {
    initialized.value = true
  }

  return currentUser.value
}

export async function logout() {
  try {
    await api.post('/auth/logout')
  } finally {
    currentUser.value = null
    initialized.value = true
  }
}