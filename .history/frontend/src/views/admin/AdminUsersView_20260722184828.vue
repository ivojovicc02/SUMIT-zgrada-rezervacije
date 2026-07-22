<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue'
import {
  createAdmin,
  getAdmins,
  updateAdmin,
} from '../../services/admin/adminService'

const admins = ref([])
const isLoading = ref(true)
const isSaving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const searchQuery = ref('')

const isModalOpen = ref(false)
const editingAdmin = ref(null)

const form = reactive({
  username: '',
  email: '',
  password: '',
  is_active: true,
})

const fieldErrors = reactive({
  username: '',
  email: '',
  password: '',
})

const filteredAdmins = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  if (!query) {
    return admins.value
  }

  return admins.value.filter((admin) => {
    return (
      admin.username?.toLowerCase().includes(query) ||
      admin.email?.toLowerCase().includes(query)
    )
  })
})

const modalTitle = computed(() => {
  return editingAdmin.value
    ? 'Uredi administratora'
    : 'Dodaj administratora'
})

const submitButtonText = computed(() => {
  if (isSaving.value) {
    return 'Spremanje...'
  }

  return editingAdmin.value
    ? 'Spremi promjene'
    : 'Kreiraj administratora'
})

async function loadAdmins() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await getAdmins()
    admins.value = Array.isArray(response.data)
      ? response.data
      : []
  } catch (error) {
    console.error(
      'Greška pri dohvaćanju administratora:',
      error,
    )

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće dohvatiti administratore.'
  } finally {
    isLoading.value = false
  }
}

function resetForm() {
  form.username = ''
  form.email = ''
  form.password = ''
  form.is_active = true

  fieldErrors.username = ''
  fieldErrors.email = ''
  fieldErrors.password = ''
}

function openCreateModal() {
  editingAdmin.value = null
  resetForm()
  isModalOpen.value = true
}

function openEditModal(admin) {
  editingAdmin.value = admin

  form.username = admin.username || ''
  form.email = admin.email || ''
  form.password = ''
  form.is_active = Boolean(admin.is_active)

  fieldErrors.username = ''
  fieldErrors.email = ''
  fieldErrors.password = ''

  isModalOpen.value = true
}

function closeModal(force = false) {
  if (isSaving.value && !force) {
    return
  }

  isModalOpen.value = false
  editingAdmin.value = null
  resetForm()
}

function validateForm() {
  fieldErrors.username = ''
  fieldErrors.email = ''
  fieldErrors.password = ''

  const username = form.username.trim()
  const email = form.email.trim()
  const password = form.password

  if (username.length < 3) {
    fieldErrors.username =
      'Korisničko ime mora imati najmanje 3 znaka.'
  }

  if (
    email &&
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  ) {
    fieldErrors.email =
      'Unesite ispravnu email adresu.'
  }

  if (!editingAdmin.value && password.length < 8) {
    fieldErrors.password =
      'Lozinka mora imati najmanje 8 znakova.'
  }

  if (
    editingAdmin.value &&
    password &&
    password.length < 8
  ) {
    fieldErrors.password =
      'Nova lozinka mora imati najmanje 8 znakova.'
  }

  return !(
    fieldErrors.username ||
    fieldErrors.email ||
    fieldErrors.password
  )
}

async function submitForm() {
  if (!validateForm()) {
    return
  }

  isSaving.value = true
  errorMessage.value = ''
  successMessage.value = ''

  const payload = {
    username: form.username.trim(),
    email: form.email.trim() || null,
  }

  if (editingAdmin.value) {
    payload.is_active = form.is_active

    if (form.password) {
      payload.password = form.password
    }
  } else {
    payload.password = form.password
  }

  try {
    if (editingAdmin.value) {
      await updateAdmin(
        editingAdmin.value.id,
        payload,
      )

      successMessage.value =
        'Administrator je uspješno ažuriran.'
    } else {
      await createAdmin(payload)

      successMessage.value =
        'Administrator je uspješno kreiran.'
    }

    closeModal()
    await loadAdmins()
  } catch (error) {
    console.error(
      'Greška pri spremanju administratora:',
      error,
    )

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće spremiti administratora.'
  } finally {
    isSaving.value = false
  }
}

async function toggleAdminStatus(admin) {
  const nextStatus = !admin.is_active

  const action = nextStatus
    ? 'aktivirati'
    : 'deaktivirati'

  const confirmed = window.confirm(
    `Želite li ${action} administratora "${admin.username}"?`,
  )

  if (!confirmed) {
    return
  }

  errorMessage.value = ''
  successMessage.value = ''

  try {
    await updateAdmin(admin.id, {
      is_active: nextStatus,
    })

    successMessage.value = nextStatus
      ? 'Administrator je aktiviran.'
      : 'Administrator je deaktiviran.'

    await loadAdmins()
  } catch (error) {
    console.error(
      'Greška pri promjeni statusa administratora:',
      error,
    )

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće promijeniti status administratora.'
  }
}

onMounted(() => {
  loadAdmins()
})
</script>

<template>
  <section class="admins-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">
          Upravljanje pristupom
        </p>

        <h1>Administratori</h1>

        <p class="description">
          Pregledaj, kreiraj i uređuj administratorske
          račune.
        </p>
      </div>

      <button
        type="button"
        class="primary-button"
        @click="openCreateModal"
      >
        <span>+</span>
        Dodaj administratora
      </button>
    </header>

    <div
      v-if="successMessage"
      class="message message--success"
    >
      {{ successMessage }}
    </div>

    <div
      v-if="errorMessage"
      class="message message--error"
    >
      {{ errorMessage }}
    </div>

    <section class="toolbar-card">
      <div class="search-group">
        <label for="admin-search">
          Pretraga
        </label>

        <input
          id="admin-search"
          v-model="searchQuery"
          type="search"
          placeholder="Korisničko ime ili email"
        />
      </div>

      <div class="toolbar-summary">
        <span>Ukupno administratora</span>

        <strong>{{ admins.length }}</strong>
      </div>
    </section>

    <section class="table-card">
      <div
        v-if="isLoading"
        class="state-box"
      >
        Učitavanje administratora...
      </div>

      <div
        v-else-if="!filteredAdmins.length"
        class="state-box"
      >
        Nema pronađenih administratora.
      </div>

      <div
        v-else
        class="table-wrapper"
      >
        <table class="admins-table">
          <thead>
            <tr>
              <th>Administrator</th>
              <th>Email</th>
              <th>Uloga</th>
              <th>Status</th>
              <th class="actions-heading">
                Akcije
              </th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="admin in filteredAdmins"
              :key="admin.id"
            >
              <td>
                <div class="admin-identity">
                  <div class="avatar">
                    {{
                      admin.username
                        ?.charAt(0)
                        .toUpperCase()
                    }}
                  </div>

                  <div>
                    <strong>
                      {{ admin.username }}
                    </strong>

                    <span>ID: {{ admin.id }}</span>
                  </div>
                </div>
              </td>

              <td>
                {{ admin.email || 'Nije uneseno' }}
              </td>

              <td>
                <span class="role-badge">
                  Administrator
                </span>
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="{
                    'status-badge--active':
                      admin.is_active,
                    'status-badge--inactive':
                      !admin.is_active,
                  }"
                >
                  {{
                    admin.is_active
                      ? 'Aktivan'
                      : 'Neaktivan'
                  }}
                </span>
              </td>

              <td>
                <div class="actions">
                  <button
                    type="button"
                    class="action-button"
                    @click="openEditModal(admin)"
                  >
                    Uredi
                  </button>

                  <button
                    type="button"
                    class="action-button"
                    :class="{
                      'action-button--danger':
                        admin.is_active,
                      'action-button--success':
                        !admin.is_active,
                    }"
                    @click="toggleAdminStatus(admin)"
                  >
                    {{
                      admin.is_active
                        ? 'Deaktiviraj'
                        : 'Aktiviraj'
                    }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div
      v-if="isModalOpen"
      class="modal-backdrop"
      @click.self="closeModal"
    >
      <section
        class="modal-card"
        role="dialog"
        aria-modal="true"
        :aria-label="modalTitle"
      >
        <div class="modal-header">
          <div>
            <p class="eyebrow">
              Administratorski račun
            </p>

            <h2>{{ modalTitle }}</h2>
          </div>

          <button
            type="button"
            class="close-button"
            aria-label="Zatvori"
            @click="closeModal"
          >
            ×
          </button>
        </div>

        <form
          class="admin-form"
          @submit.prevent="submitForm"
        >
          <div class="form-group">
            <label for="admin-username">
              Korisničko ime
            </label>

            <input
              id="admin-username"
              v-model="form.username"
              type="text"
              autocomplete="username"
              placeholder="npr. ivan.admin"
            />

            <span
              v-if="fieldErrors.username"
              class="field-error"
            >
              {{ fieldErrors.username }}
            </span>
          </div>

          <div class="form-group">
            <label for="admin-email">
              Email adresa
            </label>

            <input
              id="admin-email"
              v-model="form.email"
              type="email"
              autocomplete="email"
              placeholder="admin@example.com"
            />

            <span
              v-if="fieldErrors.email"
              class="field-error"
            >
              {{ fieldErrors.email }}
            </span>
          </div>

          <div class="form-group">
            <label for="admin-password">
              {{
                editingAdmin
                  ? 'Nova lozinka'
                  : 'Lozinka'
              }}
            </label>

            <input
              id="admin-password"
              v-model="form.password"
              type="password"
              :autocomplete="
                editingAdmin
                  ? 'new-password'
                  : 'new-password'
              "
              :placeholder="
                editingAdmin
                  ? 'Ostavi prazno bez promjene'
                  : 'Najmanje 8 znakova'
              "
            />

            <span
              v-if="fieldErrors.password"
              class="field-error"
            >
              {{ fieldErrors.password }}
            </span>
          </div>

          <label
            v-if="editingAdmin"
            class="switch-row"
          >
            <input
              v-model="form.is_active"
              type="checkbox"
            />

            <span>
              Administrator je aktivan
            </span>
          </label>

          <div class="modal-actions">
            <button
              type="button"
              class="secondary-button"
              :disabled="isSaving"
              @click="closeModal"
            >
              Odustani
            </button>

            <button
              type="submit"
              class="primary-button"
              :disabled="isSaving"
            >
              {{ submitButtonText }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </section>
</template>

<style scoped>
.admins-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.page-header h1,
.modal-header h2 {
  margin: 0;
  color: #0f172a;
}

.page-header h1 {
  font-size: clamp(26px, 3vw, 36px);
}

.description {
  margin: 8px 0 0;
  color: #64748b;
}

.primary-button,
.secondary-button,
.action-button,
.close-button {
  border: 0;
  font: inherit;
  cursor: pointer;
}

.primary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 16px;
  border-radius: 10px;
  background: #2563eb;
  color: white;
  font-weight: 700;
}

.primary-button:disabled,
.secondary-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.toolbar-card,
.table-card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: white;
  box-shadow: 0 8px 24px rgb(15 23 42 / 5%);
}

.toolbar-card {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 20px;
  padding: 18px 20px;
}

.search-group {
  display: flex;
  width: min(420px, 100%);
  flex-direction: column;
  gap: 7px;
}

.search-group label,
.form-group label {
  color: #475569;
  font-size: 13px;
  font-weight: 700;
}

.search-group input,
.form-group input {
  width: 100%;
  box-sizing: border-box;
  padding: 11px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 9px;
  background: white;
  color: #0f172a;
  font: inherit;
  outline: none;
}

.search-group input:focus,
.form-group input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgb(37 99 235 / 12%);
}

.toolbar-summary {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.toolbar-summary span {
  color: #94a3b8;
  font-size: 12px;
}

.toolbar-summary strong {
  color: #0f172a;
  font-size: 22px;
}

.table-card {
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.admins-table {
  width: 100%;
  border-collapse: collapse;
}

.admins-table th {
  padding: 15px 18px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  font-size: 11px;
  text-align: left;
  text-transform: uppercase;
}

.admins-table td {
  min-width: 120px;
  padding: 16px 18px;
  border-bottom: 1px solid #f1f5f9;
  color: #64748b;
  font-size: 13px;
}

.admins-table tbody tr:last-child td {
  border-bottom: 0;
}

.admin-identity {
  display: flex;
  align-items: center;
  gap: 11px;
}

.avatar {
  display: grid;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  place-items: center;
  border-radius: 12px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 15px;
  font-weight: 800;
}

.admin-identity strong,
.admin-identity span {
  display: block;
}

.admin-identity strong {
  color: #0f172a;
}

.admin-identity span {
  margin-top: 3px;
  color: #94a3b8;
  font-size: 11px;
}

.role-badge,
.status-badge {
  display: inline-flex;
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.role-badge {
  background: #eff6ff;
  color: #1d4ed8;
}

.status-badge--active {
  background: #ecfdf5;
  color: #047857;
}

.status-badge--inactive {
  background: #f1f5f9;
  color: #64748b;
}

.actions-heading {
  text-align: right !important;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.action-button {
  padding: 8px 10px;
  border-radius: 8px;
  background: #f1f5f9;
  color: #334155;
  font-size: 12px;
  font-weight: 700;
}

.action-button--danger {
  background: #fff1f2;
  color: #be123c;
}

.action-button--success {
  background: #ecfdf5;
  color: #047857;
}

.state-box {
  display: grid;
  min-height: 240px;
  place-items: center;
  padding: 24px;
  color: #94a3b8;
  text-align: center;
}

.message {
  padding: 13px 16px;
  border-radius: 11px;
  font-size: 13px;
  font-weight: 600;
}

.message--success {
  border: 1px solid #a7f3d0;
  background: #ecfdf5;
  color: #047857;
}

.message--error {
  border: 1px solid #fecdd3;
  background: #fff1f2;
  color: #be123c;
}

.modal-backdrop {
  position: fixed;
  z-index: 1000;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgb(15 23 42 / 48%);
}

.modal-card {
  width: min(560px, 100%);
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  border-radius: 18px;
  background: white;
  box-shadow: 0 24px 70px rgb(15 23 42 / 30%);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 22px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.close-button {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: #f1f5f9;
  color: #475569;
  font-size: 22px;
}

.admin-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 22px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.field-error {
  color: #be123c;
  font-size: 12px;
}

.switch-row {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #334155;
  font-size: 13px;
  font-weight: 600;
}

.switch-row input {
  width: 17px;
  height: 17px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 4px;
}

.secondary-button {
  padding: 11px 16px;
  border-radius: 10px;
  background: #f1f5f9;
  color: #334155;
  font-weight: 700;
}

@media (max-width: 760px) {
  .page-header,
  .toolbar-card {
    flex-direction: column;
  }

  .primary-button {
    width: 100%;
  }

  .toolbar-summary {
    align-items: flex-start;
  }

  .actions {
    justify-content: flex-start;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions button {
    width: 100%;
  }
}
</style>
