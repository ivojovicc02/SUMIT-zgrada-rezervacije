<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const email = ref('')
const password = ref('')
const errorMessage = ref('')

const handleLogin = () => {
  if (!email.value || !password.value) {
    errorMessage.value = 'Unesite e-mail i lozinku.'
    return
  }

  // Privremeno dok backend autentikacija nije povezana.
  localStorage.setItem('admin_token', 'temporary-admin-token')

  router.push({ name: 'admin-dashboard' })
}
</script>

<template>
  <main class="login-page">
    <form class="login-card" @submit.prevent="handleLogin">
      <div>
        <p class="subtitle">SUMIT centar</p>
        <h1>Administratorska prijava</h1>
        <p>Prijavite se za upravljanje rezervacijama i prostorima.</p>
      </div>

      <label>
        E-mail
        <input
          v-model="email"
          type="email"
          placeholder="admin@sumit.ba"
        />
      </label>

      <label>
        Lozinka
        <input
          v-model="password"
          type="password"
          placeholder="Unesite lozinku"
        />
      </label>

      <p v-if="errorMessage" class="error">
        {{ errorMessage }}
      </p>

      <button type="submit">
        Prijavi se
      </button>
    </form>
  </main>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: #f4f6f8;
}

.login-card {
  width: min(100%, 420px);
  display: grid;
  gap: 20px;
  padding: 32px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 12px 35px rgb(0 0 0 / 8%);
}

.subtitle {
  margin: 0;
  font-weight: 700;
}

h1 {
  margin: 6px 0;
}

label {
  display: grid;
  gap: 8px;
  font-weight: 600;
}

input {
  padding: 12px;
  border: 1px solid #ccd2d8;
  border-radius: 8px;
  font: inherit;
}

button {
  padding: 12px;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

.error {
  margin: 0;
}
</style>