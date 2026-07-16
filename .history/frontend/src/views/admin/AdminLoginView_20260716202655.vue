<script setup>
import { ref } from 'vue'
import {
  useRoute,
  useRouter,
} from 'vue-router'
import { login } from '../../services/admin/authService'

const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''
  loading.value = true

  try {
    await login(
      username.value,
      password.value,
    )

    const redirectPath =
      typeof route.query.redirect === 'string'
        ? route.query.redirect
        : '/admin'

    await router.replace(redirectPath)
  } catch (error) {
    if (error.response?.status === 401) {
      errorMessage.value =
        'Pogrešno korisničko ime ili lozinka.'
    } else if (error.response?.status === 422) {
      errorMessage.value =
        'Provjerite unesene podatke.'
    } else if (error.response?.data?.detail) {
      errorMessage.value =
        typeof error.response.data.detail === 'string'
          ? error.response.data.detail
          : 'Došlo je do pogreške pri prijavi.'
    } else if (error.code === 'ERR_NETWORK') {
      errorMessage.value =
        'Nije moguće povezati se s backendom.'
    } else {
      errorMessage.value =
        'Došlo je do pogreške prilikom prijave.'
    }

    console.error('Login greška:', error)
  } finally {
    loading.value = false
  }
}
</script>
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

