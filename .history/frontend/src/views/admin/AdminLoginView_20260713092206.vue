ž<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  isAdmin,
  login,
  logout,
} from '../../services/authService'

const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  loading.value = true
  errorMessage.value = ''

  try {
    await login(
      email.value.trim(),
      password.value,
    )

    if (!isAdmin()) {
      await logout()
      errorMessage.value =
        'Nemate administratorska prava.'
      return
    }

    const redirect =
      typeof route.query.redirect === 'string'
        ? route.query.redirect
        : '/admin'

    await router.replace(redirect)
  } catch (error) {
    if (error.response?.status === 401) {
      errorMessage.value =
        'Email ili lozinka nisu ispravni.'
    } else if (error.response?.status === 403) {
      errorMessage.value =
        'Nemate administratorska prava.'
    } else {
      errorMessage.value =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        'Prijava trenutno nije moguća.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <form
      class="login-form"
      @submit.prevent="handleLogin"
    >
      <h1>SUMIT administracija</h1>

      <p v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </p>

      <label for="email">Email</label>

      <input
        id="email"
        v-model="email"
        type="email"
        autocomplete="email"
        required
        :disabled="loading"
      />

      <label for="password">Lozinka</label>

      <input
        id="password"
        v-model="password"
        type="password"
        autocomplete="current-password"
        required
        :disabled="loading"
      />

      <button type="submit" :disabled="loading">
        {{ loading ? 'Prijava...' : 'Prijavi se' }}
      </button>
    </form>
  </main>
</template>