<template>
  <main class="admin-login-page">
    <section class="admin-login-card">
      <div class="admin-login-header">
          <img
            src="../../assets/sumit-logo.png"
            alt="SUMIT"
            class="admin-login-logo"
          />
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