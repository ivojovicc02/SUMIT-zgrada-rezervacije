```vue
<script setup>
import { computed, onMounted, ref } from 'vue'
import { getSpaces } from '@/services/spaceService'
import '@/assets/styles/admin-spaces.css'

const searchQuery = ref('')
const selectedCategory = ref('')

const spaces = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const fallbackImage =
  'https://placehold.co/240x160?text=Nema+slike'

async function fetchSpaces() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await getSpaces()

    spaces.value = Array.isArray(response.data)
      ? response.data
      : []
  } catch (error) {
    console.error('Greška pri dohvatu prostora:', error)

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće dohvatiti prostore.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchSpaces)

const filteredSpaces = computed(() => {
  const normalizedSearch = searchQuery.value
    .trim()
    .toLowerCase()

  return spaces.value.filter((space) => {
    const name = space.name?.toLowerCase() || ''
    const description =
      space.description?.toLowerCase() || ''

    const matchesSearch =
      !normalizedSearch ||
      name.includes(normalizedSearch) ||
      description.includes(normalizedSearch)

    const matchesCategory =
      !selectedCategory.value ||
      space.space_type === selectedCategory.value

    return matchesSearch && matchesCategory
  })
})

const totalCapacity = computed(() => {
  return spaces.value.reduce((sum, space) => {
    return sum + Number(space.capacity || 0)
  }, 0)
})

const spaceTypesCount = computed(() => {
  const types = spaces.value
    .map((space) => space.space_type)
    .filter(Boolean)

  return new Set(types).size
})

const availableSpaceTypes = computed(() => {
  const types = spaces.value
    .map((space) => space.space_type)
    .filter(Boolean)

  return [...new Set(types)].sort()
})

function getPrimaryImage(space) {
  if (!Array.isArray(space.images)) {
    return fallbackImage
  }

  const primaryImage = space.images.find(
    (image) =>
      image.is_primary === true ||
      image.is_primary === 1,
  )

  return (
    primaryImage?.url ||
    space.images[0]?.url ||
    fallbackImage
  )
}

function handleImageError(event) {
  event.target.src = fallbackImage
}

function formatSpaceType(spaceType) {
  if (!spaceType) {
    return 'Nije definirano'
  }

  const typeLabels = {
    office: 'Ured i radni prostor',
    workspace: 'Radni prostor',
    conference: 'Konferencijska dvorana',
    conference_room: 'Konferencijska dvorana',
    meeting_room: 'Sala za sastanke',
    outdoor: 'Vanjski prostor',
    park: 'Park',
  }

  return typeLabels[spaceType] || spaceType
}

function formatPrice(price) {
  const numericPrice = Number(price)

  if (Number.isNaN(numericPrice)) {
    return '0,00'
  }

  return new Intl.NumberFormat('hr-HR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numericPrice)
}

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
        <h1>Prostori</h1>

        <p class="page-description">
          Upravljajte uredima, konferencijskim dvoranama
          i vanjskim prostorima SUMIT zgrade.
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
            <circle cx="9" cy="8" r="3" />
            <path d="M3 20v-2a6 6 0 0 1 12 0v2" />
            <path
              d="M16 5a3 3 0 0 1 0 6M17 14a5 5 0 0 1 4 5v1"
            />
          </svg>
        </div>

        <div class="summary-content">
          <span>Ukupan kapacitet</span>
          <strong>{{ totalCapacity }}</strong>
        </div>
      </article>

      <article class="summary-card">
        <div class="summary-icon summary-icon--orange">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </div>

        <div class="summary-content">
          <span>Vrsta prostora</span>
          <strong>{{ spaceTypesCount }}</strong>
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
            aria-label="Vrsta prostora"
          >
            <option value="">Sve vrste prostora</option>

            <option
              v-for="spaceType in availableSpaceTypes"
              :key="spaceType"
              :value="spaceType"
            >
              {{ formatSpaceType(spaceType) }}
            </option>
          </select>
        </div>
      </div>

      <div
        v-if="isLoading"
        class="spaces-state"
      >
        <div class="loading-spinner"></div>
        <p>Učitavanje prostora...</p>
      </div>

      <div
        v-else-if="errorMessage"
        class="spaces-state spaces-state--error"
      >
        <h3>Dogodila se greška</h3>
        <p>{{ errorMessage }}</p>

        <button
          type="button"
          class="retry-button"
          @click="fetchSpaces"
        >
          Pokušaj ponovno
        </button>
      </div>

      <div v-else class="table-wrapper">
        <table class="spaces-table">
          <thead>
            <tr>
              <th>Prostor</th>
              <th>Vrsta</th>
              <th>Kapacitet</th>
              <th>Cijena</th>
              <th>Oprema</th>
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
                    :src="getPrimaryImage(space)"
                    :alt="space.name"
                    @error="handleImageError"
                  />

                  <div class="space-info-content">
                    <strong>
                      {{ space.name || 'Prostor bez naziva' }}
                    </strong>

                    <span
                      v-if="space.description"
                      class="space-description"
                      :title="space.description"
                    >
                      {{ space.description }}
                    </span>

                    <span class="space-id">
                      ID: #{{ space.id }}
                    </span>
                  </div>
                </div>
              </td>

              <td>
                <span class="category-text">
                  {{ formatSpaceType(space.space_type) }}
                </span>
              </td>

              <td>
                <div class="capacity">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="9" cy="8" r="3" />

                    <path
                      d="M3 20v-2a6 6 0 0 1 12 0v2"
                    />

                    <path
                      d="M16 5a3 3 0 0 1 0 6M17 14a5 5 0 0 1 4 5v1"
                    />
                  </svg>

                  {{ space.capacity }} osoba
                </div>
              </td>

              <td>
                <div class="price">
                  <strong>
                    {{ formatPrice(space.price_per_hour) }} KM
                  </strong>

                  <span>po satu</span>
                </div>
              </td>

              <td>
                <div
                  v-if="space.equipment?.length"
                  class="equipment-list"
                >
                  <span
                    v-for="equipment in space.equipment.slice(0, 2)"
                    :key="equipment.name"
                    class="equipment-badge"
                  >
                    {{ equipment.name }}
                  </span>

                  <span
                    v-if="space.equipment.length > 2"
                    class="equipment-more"
                    :title="
                      space.equipment
                        .slice(2)
                        .map((item) => item.name)
                        .join(', ')
                    "
                  >
                    +{{ space.equipment.length - 2 }}
                  </span>
                </div>

                <span v-else class="no-equipment">
                  Nema opreme
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
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        d="M4 21V3h16v18M8 7h2M14 7h2M8 11h2M14 11h2M9 21v-5h6v5"
                      />
                    </svg>
                  </div>

                  <h3>Nema pronađenih prostora</h3>

                  <p>
                    Promijenite kriterije pretrage ili
                    dodajte novi prostor.
                  </p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <footer
        v-if="!isLoading && !errorMessage"
        class="table-footer"
      >
        <span>
          Prikazano
          <strong>{{ filteredSpaces.length }}</strong>
          od
          <strong>{{ spaces.length }}</strong>
          prostora
        </span>
      </footer>
    </div>
  </section>
</template>
```
