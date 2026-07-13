import { computed, ref } from 'vue'
import api from './api'

const TOKEN_KEY = 'admin_token'
const USERNAME_KEY = 'admin_username'

export const authToken = ref(
  localStorage.getItem(TOKEN_KEY),
)

export const currentUser = ref(null)
export const initialized = ref(false)

export const isAuthenticated = computed(() =>
  Boolean(authToken.value),
)

export async function login(username, password) {
  const formData = new URLSearchParams()

  formData.append('username', username)
  formData.append('password', password)

  const response = await api.post(
    '/admin/login',
    formData,
    {
      headers: {
        'Content-Type':
          'application/x-www-form-urlencoded',
      },
    },
  )

  const token = response.data?.access_token

  if (!token) {
    throw new Error(
      'Backend nije vratio access token.',
    )
  }

  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USERNAME_KEY, username)

  authToken.value = token

  currentUser.value = {
    username,
  }

  initialized.value = true

  return currentUser.value
}

export function initializeAuth() {
  const token = localStorage.getItem(TOKEN_KEY)
  const username =
    localStorage.getItem(USERNAME_KEY)

  authToken.value = token

  currentUser.value = token
    ? {
        username: username || 'Administrator',
      }
    : null

  initialized.value = true

  return currentUser.value
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USERNAME_KEY)

  authToken.value = null
  currentUser.value = null
  initialized.value = true
}