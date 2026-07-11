<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  router.push({ name: 'admin-login' })
}
</script>

<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div>
        <h2>SUMIT Admin</h2>

        <nav>
          <RouterLink :to="{ name: 'admin-dashboard' }">
            Pregled
          </RouterLink>

          <RouterLink :to="{ name: 'admin-spaces' }">
            Prostori
          </RouterLink>

          <RouterLink :to="{ name: 'admin-reservations' }">
            Rezervacije
          </RouterLink>

          <RouterLink :to="{ name: 'admin-reports' }">
            Izvještaji
          </RouterLink>
        </nav>
      </div>

      <button type="button" @click="handleLogout">
        Odjava
      </button>
    </aside>

    <div class="admin-content">
      <header class="topbar">
        <h1>Administratorsko sučelje</h1>
      </header>

      <main class="page-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 240px 1fr;
  background: #f4f6f8;
}

.sidebar {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 24px;
  background: #ffffff;
  border-right: 1px solid #e3e7eb;
}

.sidebar h2 {
  margin-top: 0;
}

nav {
  display: grid;
  gap: 8px;
  margin-top: 32px;
}

nav a {
  padding: 11px 12px;
  color: inherit;
  text-decoration: none;
  border-radius: 8px;
}

nav a.router-link-active {
  background: #e8edf3;
  font-weight: 700;
}

.sidebar button {
  padding: 10px;
  cursor: pointer;
}

.admin-content {
  min-width: 0;
}

.topbar {
  padding: 20px 28px;
  background: white;
  border-bottom: 1px solid #e3e7eb;
}

.topbar h1 {
  margin: 0;
  font-size: 20px;
}

.page-content {
  padding: 28px;
}

@media (max-width: 768px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    gap: 20px;
    border-right: 0;
    border-bottom: 1px solid #e3e7eb;
  }

  nav {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>