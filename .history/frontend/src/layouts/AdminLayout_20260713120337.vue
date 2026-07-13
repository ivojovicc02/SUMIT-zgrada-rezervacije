<template>
  <div class="admin-layout">
    <header class="admin-header">
      <RouterLink to="/admin/spaces" class="admin-logo-link">
        <img
          src="@/assets/sumit-logo.png"
          alt="SUMIT"
          class="admin-logo"
        />
      </RouterLink>

      <button
        class="admin-menu-button"
        type="button"
        aria-label="Otvori navigaciju"
        :aria-expanded="isMenuOpen"
        @click="isMenuOpen = !isMenuOpen"
      >
        ☰
      </button>
    </header>

    <nav
      v-if="isMenuOpen"
      class="admin-menu"
    >
      <RouterLink to="/admin/spaces" @click="closeMenu">
        Prostori
      </RouterLink>

      <RouterLink to="/admin/reservations" @click="closeMenu">
        Rezervacije
      </RouterLink>

      <RouterLink to="/admin/calendar" @click="closeMenu">
        Kalendar
      </RouterLink>

      <RouterLink to="/admin/reports" @click="closeMenu">
        Izvještaji
      </RouterLink>

      <button type="button" @click="handleLogout">
        Odjava
      </button>
    </nav>

    <main class="admin-content">
      <RouterView />
    </main>

    <footer class="admin-footer">
      © 2026 SUMIT — Sustav za rezervaciju prostora
    </footer>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { RouterLink, RouterView, useRouter } from "vue-router"

const router = useRouter()
const isMenuOpen = ref(false)

function closeMenu() {
  isMenuOpen.value = false
}

function handleLogout() {
  localStorage.removeItem("admin_token")
  router.push("/admin/login")
}
</script>