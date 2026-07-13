<script setup>
import { useRouter } from 'vue-router'
import {
  getCurrentUser,
  logout,
} from '../services/authService'

const router = useRouter()
const user = getCurrentUser()

async function handleLogout() {
  await logout()
  await router.replace('/admin/login')
}
</script>

<template>
  <div class="admin-layout">
    <aside>
      <h2>SUMIT Admin</h2>

      <p v-if="user">
        {{ user.firstName }} {{ user.lastName }}
      </p>

      <nav>
        <RouterLink to="/admin">
          Dashboard
        </RouterLink>

        <RouterLink to="/admin/spaces">
          Prostori
        </RouterLink>

        <RouterLink to="/admin/reservations">
          Rezervacije
        </RouterLink>

        <RouterLink to="/admin/users">
          Korisnici
        </RouterLink>
      </nav>

      <button type="button" @click="handleLogout">
        Odjava
      </button>
    </aside>

    <main>
      <RouterView />
    </main>
  </div>
</template>