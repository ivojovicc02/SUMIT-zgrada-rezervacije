<script setup>
import { ref } from 'vue'
import {
  useRoute,
  useRouter,
} from 'vue-router'
import {
  login,
} from '../../services/authService'

const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  if (loading.value) {
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    await login(
      username.value.trim(),
      password.value,
    )

    const redirect =
      typeof route.query.redirect === 'string' &&
      route.query.redirect.startsWith('/admin')
        ? route.query.redirect
        : '/admin'

    await router.replace(redirect)
  } catch (error) {
    if (error.response?.status === 401) {
      errorMessage.value =
        'Pogrešno korisničko ime ili lozinka.'
    } else if (error.response?.status === 422) {
      errorMessage.value =
        'Korisničko ime i lozinka su obavezni.'
    } else if (!error.response) {
      errorMessage.value =
        'Nije moguće povezati se s backendom.'
    } else {
      errorMessage.value =
        error.response?.data?.detail ||
        error.message ||
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

      <p>
        Prijavite se za pristup upravljanju
        rezervacijama.
      </p>

      <p
        v-if="errorMessage"
        class="error-message"
        role="alert"
      >
        {{ errorMessage }}
      </p>

      <div class="form-group">
        <label for="username">
          Korisničko ime
        </label>

        <input
          id="username"
          v-model.trim="username"
          type="text"
          autocomplete="username"
          required
          :disabled="loading"
        />
      </div>

      <div class="form-group">
        <label for="password">
          Lozinka
        </label>

        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
          :disabled="loading"
        />
      </div>

      <button
        type="submit"
        :disabled="loading"
      >
        {{
          loading
            ? 'Prijava...'
            : 'Prijavi se'
        }}
      </button>
    </form>
  </main>
</template>