<template>
  <div class="admin-layout">
    <header class="admin-header">
      <RouterLink to="/admin/spaces" class="admin-logo-link">
        <img
          src="../assets/sumit-logo.png"
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
  <span></span>
  <span></span>
  <span></span>
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
  <div class="admin-footer-content">
    <div class="admin-footer-brand">
      <img
        src="../assets/sumit-logo.png"
        alt="SUMIT"
        class="admin-footer-logo"
      />

      <p>
        Centar za informacijske tehnologije
        <br />
        Sveučilišta u Mostaru — SUMIT
      </p>
    </div>

    <div class="admin-footer-contact">
      <h3>Kontakt</h3>

      <address>
        Trg hrvatskih velikana 1
        <br />
        88000 Mostar
        <br />
        Bosna i Hercegovina
      </address>

      <a href="mailto:sumit@sum.ba">
        sumit@sum.ba
      </a>

      <a href="tel:+38763047074">
        +387 (63) 047 074
      </a>
    </div>

    <div class="admin-footer-links">
      <h3>Administracija</h3>

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
    </div>
  </div>

  <div class="admin-footer-bottom">
    <p>
      © {{ new Date().getFullYear() }}
      Sveučilište u Mostaru — Sva prava pridržana
    </p>
  </div>
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