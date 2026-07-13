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
<template>
  <main class="admin-login-page">
    <section class="admin-login-card">
      <div class="admin-login-header">
  <img
    src="../../assets/sumit-logo.png"
    alt="SUMIT"
    class="admin-login-logo"
  />

  <p class="admin-login-subtitle">
    Administratorsko sučelje za upravljanje prostorima,
    rezervacijama i izvještajima SUMIT zgrade.
  </p>
</div>
      <form
        class="admin-login-form"
        @submit.prevent="handleLogin"
      >
        <p
          v-if="errorMessage"
          class="admin-login-error"
          role="alert"
        >
          {{ errorMessage }}
        </p>

        <div class="admin-login-field">
          <label for="username">
            Korisničko ime
          </label>

          <input
            id="username"
            v-model.trim="username"
            type="text"
            autocomplete="username"
            placeholder="Unesite korisničko ime"
            required
            :disabled="loading"
          />
        </div>

        <div class="admin-login-field">
          <label for="password">
            Lozinka
          </label>

          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="Unesite lozinku"
            required
            :disabled="loading"
          />
        </div>

        <button
          class="admin-login-button"
          type="submit"
          :disabled="loading"
        >
          {{ loading ? 'Prijava...' : 'Prijavi se' }}
        </button>
      </form>
    </section>
  </main>
</template>