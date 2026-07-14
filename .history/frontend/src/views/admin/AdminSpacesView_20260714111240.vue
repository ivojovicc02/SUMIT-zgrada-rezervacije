<script setup>
import { computed, ref } from 'vue'

const searchQuery = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')

const spaces = ref([
  {
    id: 1,
    name: 'Konferencijska dvorana A',
    category: 'Konferencijska dvorana',
    capacity: 120,
    price: 180,
    priceUnit: 'sat',
    status: 'active',
    image:
      'https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=500&q=80',
  },
  {
    id: 2,
    name: 'Privatni ured 01',
    category: 'Ured i radni prostor',
    capacity: 6,
    price: 45,
    priceUnit: 'sat',
    status: 'active',
    image:
      'https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=500&q=80',
  },
  {
    id: 3,
    name: 'SUMIT terasa',
    category: 'Vanjski prostor',
    capacity: 80,
    price: 250,
    priceUnit: 'termin',
    status: 'inactive',
    image:
      'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=500&q=80',
  },
  {
    id: 4,
    name: 'Sala za sastanke B',
    category: 'Ured i radni prostor',
    capacity: 14,
    price: 75,
    priceUnit: 'sat',
    status: 'active',
    image:
      'https://images.unsplash.com/photo-1517502884422-41eaead166d4?auto=format&fit=crop&w=500&q=80',
  },
])

const filteredSpaces = computed(() => {
  return spaces.value.filter((space) => {
    const matchesSearch = space.name
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase())

    const matchesCategory =
      !selectedCategory.value ||
      space.category === selectedCategory.value

    const matchesStatus =
      !selectedStatus.value ||
      space.status === selectedStatus.value

    return matchesSearch && matchesCategory && matchesStatus
  })
})

const activeSpacesCount = computed(() => {
  return spaces.value.filter((space) => space.status === 'active').length
})

function openCreateSpace() {
  console.log('Otvori formu za dodavanje prostora')
}

function editSpace(space) {
  console.log('Uredi prostor:', space)
}

function openCalendar(space) {
  console.log('Otvori kalendar prostora:', space)
}

function deleteSpace(space) {
  console.log('Obriši prostor:', space)
}
</script>

<template>
  <section class="spaces-page">
    <header class="page-header">
      <div>
        <p class="page-eyebrow">Administracija</p>

        <h1>Prostori</h1>

        <p class="page-description">
          Upravljajte uredima, konferencijskim dvoranama i vanjskim
          prostorima SUMIT zgrade.
        </p>
      </div>

      <button
        class="primary-button"
        type="button"
        @click="openCreateSpace"
      >
        <span class="button-icon">+</span>
        Dodaj prostor
      </button>
    </header>

    <div class="summary-grid">
      <article class="summary-card">
        <div class="summary-icon summary-icon--blue">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M4 21V3h16v18M8 7h2M14 7h2M8 11h2M14 11h2M9 21v-5h6v5"
            />
          </svg>
        </div>

        <div class="summary-content">
          <span>Ukupno prostora</span>
          <strong>{{ spaces.length }}</strong>
        </div>
      </article>

      <article class="summary-card">
        <div class="summary-icon summary-icon--green">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="m5 12 4 4L19 6" />
          </svg>
        </div>

        <div class="summary-content">
          <span>Aktivni prostori</span>
          <strong>{{ activeSpacesCount }}</strong>
        </div>
      </article>

      <article class="summary-card">
        <div class="summary-icon summary-icon--orange">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M8 2v3M16 2v3M3 9h18M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2Z"
            />
          </svg>
        </div>

        <div class="summary-content">
          <span>Rezervirani danas</span>
          <strong>3</strong>
        </div>
      </article>
    </div>

    <div class="spaces-panel">
      <div class="toolbar">
        <div class="search-field">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-4-4" />
          </svg>

          <input
            v-model="searchQuery"
            type="search"
            placeholder="Pretraži prostore..."
          />
        </div>

        <div class="filters">
          <select
            v-model="selectedCategory"
            aria-label="Kategorija prostora"
          >
            <option value="">Sve kategorije</option>

            <option value="Ured i radni prostor">
              Uredi i radni prostori
            </option>

            <option value="Konferencijska dvorana">
              Konferencijske dvorane
            </option>

            <option value="Vanjski prostor">
              Vanjski prostori
            </option>
          </select>

          <select
            v-model="selectedStatus"
            aria-label="Status prostora"
          >
            <option value="">Svi statusi</option>
            <option value="active">Aktivni</option>
            <option value="inactive">Neaktivni</option>
          </select>
        </div>
      </div>

      <div class="table-wrapper">
        <table class="spaces-table">
          <thead>
            <tr>
              <th>Prostor</th>
              <th>Kategorija</th>
              <th>Kapacitet</th>
              <th>Cijena</th>
              <th>Status</th>
              <th class="actions-heading">Akcije</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="space in filteredSpaces"
              :key="space.id"
            >
              <td>
                <div class="space-info">
                  <img
                    class="space-image"
                    :src="space.image"
                    :alt="space.name"
                  />

                  <div>
                    <strong>{{ space.name }}</strong>
                    <span>ID: #{{ space.id }}</span>
                  </div>
                </div>
              </td>

              <td>
                <span class="category-text">
                  {{ space.category }}
                </span>
              </td>

              <td>
                <div class="capacity">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="9" cy="8" r="3" />

                    <path d="M3 20v-2a6 6 0 0 1 12 0v2" />

                    <path
                      d="M16 5a3 3 0 0 1 0 6M17 14a5 5 0 0 1 4 5v1"
                    />
                  </svg>

                  {{ space.capacity }} osoba
                </div>
              </td>

              <td>
                <div class="price">
                  <strong>{{ space.price }} KM</strong>
                  <span>po {{ space.priceUnit }}</span>
                </div>
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="{
                    'status-badge--active':
                      space.status === 'active',
                    'status-badge--inactive':
                      space.status === 'inactive',
                  }"
                >
                  <span class="status-dot"></span>

                  {{
                    space.status === 'active'
                      ? 'Aktivan'
                      : 'Neaktivan'
                  }}
                </span>
              </td>

              <td>
                <div class="actions">
                  <button
                    class="icon-button"
                    type="button"
                    title="Otvori kalendar"
                    @click="openCalendar(space)"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        d="M8 2v3M16 2v3M3 9h18M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2Z"
                      />
                    </svg>
                  </button>

                  <button
                    class="icon-button"
                    type="button"
                    title="Uredi prostor"
                    @click="editSpace(space)"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        d="m14 4 6 6M4 20l3.5-.7L19 7.8a2.1 2.1 0 0 0-3-3L4.7 16.3 4 20Z"
                      />
                    </svg>
                  </button>

                  <button
                    class="icon-button icon-button--danger"
                    type="button"
                    title="Obriši prostor"
                    @click="deleteSpace(space)"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        d="M4 7h16M9 7V4h6v3M7 7l1 13h8l1-13"
                      />

                      <path d="M10 11v5M14 11v5" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="filteredSpaces.length === 0">
              <td colspan="6">
                <div class="empty-state">
                  <div class="empty-state-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        d="M4 21V3h16v18M8 7h2M14 7h2M8 11h2M14 11h2M9 21v-5h6v5"
                      />
                    </svg>
                  </div>

                  <h3>Nema pronađenih prostora</h3>

                  <p>
                    Promijenite kriterije pretrage ili dodajte novi
                    prostor.
                  </p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <footer class="table-footer">
        <span>
          Prikazano
          <strong>{{ filteredSpaces.length }}</strong>
          od
          <strong>{{ spaces.length }}</strong>
          prostora
        </span>

        <div class="pagination">
          <button type="button" disabled>
            Prethodna
          </button>

          <button
            type="button"
            class="pagination-active"
          >
            1
          </button>

          <button type="button">
            Sljedeća
          </button>
        </div>
      </footer>
    </div>
  </section>
</template>