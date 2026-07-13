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
  <div class="admin-footer-content">
    <section class="admin-footer-about">
      <h2>SUMIT rezervacije</h2>

      <p>
        Administratorsko sučelje za upravljanje prostorima,
        rezervacijama, terminima i izvještajima SUMIT centra.
      </p>
    </section>

    <section class="admin-footer-section">
      <h3>Administracija</h3>

      <nav class="admin-footer-navigation">
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
    </section>

    <section class="admin-footer-section">
      <h3>Kontakt</h3>

      <address class="admin-footer-contact">
        <span>
          Centar za informacijske tehnologije SUMIT
        </span>

        <span>
          Sveučilište u Mostaru
        </span>

        <span>
          Mostar, Bosna i Hercegovina
        </span>

        <a href="mailto:sumit@sum.ba">
          sumit@sum.ba
        </a>
      </address>
    </section>
  </div>

  <div class="admin-footer-bottom">
    <p>
      © {{ new Date().getFullYear() }}
      SUMIT — Sva prava pridržana
    </p>

    <p>
      Sustav za rezervaciju prostora
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