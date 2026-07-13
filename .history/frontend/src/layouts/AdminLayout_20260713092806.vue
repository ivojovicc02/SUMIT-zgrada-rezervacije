```vue
<script setup>
import { useRouter } from 'vue-router'
import {
  currentUser,
  logout,
} from '../services/authService'

const router = useRouter()

async function handleLogout() {
  await logout()
  await router.replace('/admin/login')
}
</script>

<template>
  <div class="admin-layout">
    <aside>
      <h2>SUMIT Admin</h2>

      <p v-if="currentUser">
        {{
          `${currentUser.firstName || ''} ${currentUser.lastName || ''}`.trim()
          || currentUser.email
        }}
      </p>

      <nav>
        <RouterLink to="/admin">
          Dashboard
        </RouterLink>

        <RouterLink to="/admin/prostori">
          Prostori
        </RouterLink>

        <RouterLink to="/admin/rezervacije">
          Rezervacije
        </RouterLink>

        <RouterLink to="/admin/izvjestaji">
          Izvještaji
        </RouterLink>
      </nav>

      <button
        type="button"
        @click="handleLogout"
      >
        Odjava
      </button>
    </aside>

    <main>
      <RouterView />
    </main>
  </div>
</template>
```
