<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  getSpaces,
  deleteSpaceById,
  getSpaceById,
} from '../../services/admin/spaceService'
import SpaceCreateModal from '../../components/admin/SpaceCreateModal.vue'

const searchQuery = ref('')
const selectedCategory = ref('')
const selectedSubtype = ref('')

const spaces = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const deletingSpaceId = ref(null)
const isCreateModalOpen = ref(false)

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  'http://127.0.0.1:8000'

const fallbackImage =
  'https://placehold.co/240x160?text=Nema+slike'

function getImageUrl(url) {
  if (!url) {
    return fallbackImage
  }

  if (
    url.startsWith('http://') ||
    url.startsWith('https://')
  ) {
    return url
  }

  const normalizedUrl = url.startsWith('/')
    ? url
    : `/${url}`

  return `${API_BASE_URL}${normalizedUrl}`
}

function getPrimaryImage(space) {
  if (!Array.isArray(space.images)) {
    return fallbackImage
  }

  const primaryImage = space.images.find(
    (image) => image.is_primary === true
  )

  const imagePath =
    primaryImage?.url ||
    space.images[0]?.url

  return getImageUrl(imagePath)
}

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
    const searchableValues = [
      space.name,
      space.name_en,
      space.description,
      space.description_en,
      space.space_type,
      space.space_subtype,
    ]

    const matchesSearch =
      !normalizedSearch ||
      searchableValues.some((value) =>
        value
          ?.toString()
          .toLowerCase()
          .includes(normalizedSearch),
      )

    const matchesCategory =
      !selectedCategory.value ||
      space.space_type === selectedCategory.value

    const matchesSubtype =
      !selectedSubtype.value ||
      space.space_subtype === selectedSubtype.value

    return (
      matchesSearch &&
      matchesCategory &&
      matchesSubtype
    )
  })
})

const totalCapacity = computed(() => {
  return spaces.value.reduce((sum, space) => {
    return sum + Number(space.capacity || 0)
  }, 0)
})

const modularSpacesCount = computed(() => {
  return spaces.value.filter(
    (space) => space.is_modular === true,
  ).length
})

const availableSpaceTypes = computed(() => {
  const types = spaces.value
    .map((space) => space.space_type)
    .filter(Boolean)

  return [...new Set(types)].sort()
})

const availableSpaceSubtypes = computed(() => {
  return spaces.value
    .filter((space) => {
      return (
        !selectedCategory.value ||
        space.space_type === selectedCategory.value
      )
    })
    .map((space) => space.space_subtype)
    .filter(Boolean)
    .filter(
      (subtype, index, array) =>
        array.indexOf(subtype) === index,
    )
    .sort()
})

function handleImageError(event) {
  event.target.src = fallbackImage
}

function formatSpaceType(spaceType) {
  const typeLabels = {
    office_workspace: 'Uredi i radni prostori',
    conference: 'Konferencijske dvorane',
    outdoor: 'Vanjski prostori i park',
  }

  return typeLabels[spaceType] || spaceType || 'Nije definirano'
}

function formatSpaceSubtype(spaceSubtype) {
  const subtypeLabels = {
    private_office: 'Privatni ured',
    permanent_workspace: 'Stalno radno mjesto',
    flexible_package: 'Fleksibilni paket',
    virtual_office: 'Virtualni ured',
    meeting_room: 'Sala za sastanke',
    conference_hall: 'Konferencijska dvorana',
    terrace: 'Terasa',
    green_park: 'Zeleni park',
  }

  return (
    subtypeLabels[spaceSubtype] ||
    spaceSubtype ||
    'Nije definirano'
  )
}

const averagePrice = computed(() => {
  if (spaces.value.length === 0) {
    return '0,00'
  }

  const totalPrice = spaces.value.reduce(
    (sum, space) => sum + Number(space.price || 0),
    0,
  )

  const average = totalPrice / spaces.value.length

  return average.toLocaleString('hr-HR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
})

function formatPriceUnit(priceUnit) {
  const unitLabels = {
    hour: 'po satu',
    day: 'po danu',
    month: 'mjesečno',
    reservation: 'po rezervaciji',
  }

  return unitLabels[priceUnit] || priceUnit || ''
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

function getEquipmentTitle(space) {
  if (!Array.isArray(space.equipment)) {
    return ''
  }

  return space.equipment
    .map((item) => item.name)
    .filter(Boolean)
    .join(', ')
}

function getServicesTitle(space) {
  if (!Array.isArray(space.services)) {
    return ''
  }

  return space.services
    .map((service) => service.name)
    .filter(Boolean)
    .join(', ')
}

function openCreateSpace() {
  isCreateModalOpen.value = true
}

function closeCreateSpace() {
  isCreateModalOpen.value = false
}

async function handleSpaceCreated() {
  await fetchSpaces()
}

function editSpace(space) {
  console.log('Uredi prostor:', space)
}

function openCalendar(space) {
  console.log('Otvori kalendar prostora:', space)
}

async function deleteSpace(space) {
  const confirmed = window.confirm(
    `Jeste li sigurni da želite obrisati prostor "${space.name}"?`,
  )

  if (!confirmed) {
    return
  }

  deletingSpaceId.value = space.id
  errorMessage.value = ''

  try {
    await deleteSpaceById(space.id)

    spaces.value = spaces.value.filter(
      (item) => item.id !== space.id,
    )

    if (selectedSpace.value?.id === space.id) {
      closeSpaceDetails()
    }
  } catch (error) {
    console.error('Greška pri brisanju prostora:', error)

    const detail = error.response?.data?.detail

    errorMessage.value =
      typeof detail === 'string'
        ? detail
        : 'Nije moguće obrisati prostor.'
  } finally {
    deletingSpaceId.value = null
  }
}

const selectedSpace = ref(null)
const isDetailsModalOpen = ref(false)

function openSpaceDetails(space) {
  selectedSpace.value = space
  isDetailsModalOpen.value = true
}

function closeSpaceDetails() {
  selectedSpace.value = null
  isDetailsModalOpen.value = false
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

            <path
              d="M3 20v-2a6 6 0 0 1 12 0v2"
            />

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
      <path
        d="M3 7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z"
      />
      <circle cx="12" cy="12" r="3" />
      <path d="M7 10a2 2 0 0 1-2 2M17 14a2 2 0 0 0 2-2" />
    </svg>
  </div>

        <div class="summary-content">
           <span>Prosječna cijena</span>
          <strong>{{ averagePrice }} KM</strong>
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
            @change="selectedSubtype = ''"
          >
            <option value="">
              Sve vrste prostora
            </option>

            <option
              v-for="spaceType in availableSpaceTypes"
              :key="spaceType"
              :value="spaceType"
            >
              {{ formatSpaceType(spaceType) }}
            </option>
          </select>

          <select
            v-model="selectedSubtype"
            aria-label="Podvrsta prostora"
          >
            <option value="">
              Sve podvrste
            </option>

            <option
              v-for="subtype in availableSpaceSubtypes"
              :key="subtype"
              :value="subtype"
            >
              {{ formatSpaceSubtype(subtype) }}
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
              <th>Oprema i usluge</th>
              <th class="actions-heading">
                Akcije
              </th>
            </tr>
          </thead>

          <tbody>
            <tr
                v-for="space in filteredSpaces"
                :key="space.id"
                class="space-row"
                tabindex="0"
                @click="openSpaceDetails(space)"
                @keydown.enter="openSpaceDetails(space)"
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
                    <div class="space-title-row">
                      <strong>
                        {{
                          space.name ||
                          'Prostor bez naziva'
                        }}
                      </strong>

                      <span
                        v-if="space.is_modular"
                        class="modular-badge"
                      >
                        Modularno
                      </span>
                    </div>

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
                <div class="space-type-cell">
                  <span class="category-text">
                    {{
                      formatSpaceType(
                        space.space_type,
                      )
                    }}
                  </span>

                  <span class="subcategory-text">
                    {{
                      formatSpaceSubtype(
                        space.space_subtype,
                      )
                    }}
                  </span>
                </div>
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
                    {{ formatPrice(space.price) }} KM
                  </strong>

                  <span>
                    {{
                      formatPriceUnit(
                        space.price_unit,
                      )
                    }}
                  </span>
                </div>
              </td>

              <td>
                <div class="details-summary">
                  <div
                    v-if="space.equipment?.length"
                    class="details-row"
                  >
                    <span class="details-label">
                      Oprema:
                    </span>

                    <div
                      class="equipment-list"
                      :title="getEquipmentTitle(space)"
                    >
                      <span
                        v-for="equipment in space.equipment.slice(0, 2)"
                        :key="equipment.id || equipment.name"
                        class="equipment-badge"
                      >
                        {{ equipment.name }}
                      </span>

                      <span
                        v-if="space.equipment.length > 2"
                        class="equipment-more"
                      >
                        +{{ space.equipment.length - 2 }}
                      </span>
                    </div>
                  </div>

                  <span
                    v-else
                    class="no-equipment"
                  >
                    Nema navedene opreme
                  </span>

                  <div
                    v-if="space.services?.length"
                    class="services-summary"
                    :title="getServicesTitle(space)"
                  >
                    <span class="details-label">
                      Usluge:
                    </span>

                    <span>
                      {{ space.services.length }}
                      dostupno
                    </span>
                  </div>
                </div>
              </td>

              <td>
                <div class="actions">
                  <button
                    class="icon-button"
                    type="button"
                    title="Otvori kalendar"
                    @click.stop="openCalendar(space)"
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
                    @click.stop="editSpace(space)"
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
                      :disabled="deletingSpaceId === space.id"
                      @click.stop="deleteSpace(space)"
                    >
                      <svg
                        v-if="deletingSpaceId !== space.id"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                      >
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

  <Teleport to="body">
  <div
    v-if="isDetailsModalOpen && selectedSpace"
    class="modal-overlay"
    @click.self="closeSpaceDetails"
  >
    <div
      class="space-details-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="space-details-title"
    >
      <header class="modal-header">
        <div>
          <div class="modal-title-row">
            <h2 id="space-details-title">
              {{ selectedSpace.name }}
            </h2>

            <span
              v-if="selectedSpace.is_modular"
              class="modular-badge"
            >
              Modularna
            </span>
          </div>

          <p>
            {{ formatSpaceSubtype(selectedSpace.space_subtype) }}
          </p>
        </div>

        <button
          class="modal-close-button"
          type="button"
          aria-label="Zatvori"
          @click="closeSpaceDetails"
        >
          ×
        </button>
      </header>

      <div class="modal-content">
        <img
          class="details-main-image"
          :src="getPrimaryImage(selectedSpace)"
          :alt="selectedSpace.name"
          @error="handleImageError"
        />

        <section class="details-section">
          <h3>Opis</h3>
          <p>{{ selectedSpace.description }}</p>
        </section>

        <div class="details-grid">
          <div class="detail-item">
            <span>Glavna kategorija</span>
            <strong>
              {{ formatSpaceType(selectedSpace.space_type) }}
            </strong>
          </div>

          <div class="detail-item">
            <span>Podvrsta</span>
            <strong>
              {{ formatSpaceSubtype(selectedSpace.space_subtype) }}
            </strong>
          </div>

          <div class="detail-item">
            <span>Kapacitet</span>
            <strong>
              {{ selectedSpace.capacity }} osoba
            </strong>
          </div>

          <div class="detail-item">
            <span>Cijena</span>
            <strong>
              {{ formatPrice(selectedSpace.price) }} KM
              {{ formatPriceUnit(selectedSpace.price_unit) }}
            </strong>
          </div>
        </div>

        <section class="details-section">
          <h3>Oprema</h3>

          <div
            v-if="selectedSpace.equipment?.length"
            class="details-tags"
          >
            <span
              v-for="equipment in selectedSpace.equipment"
              :key="equipment.id || equipment.name"
              class="equipment-badge"
            >
              {{ equipment.name }}
            </span>
          </div>

          <p v-else>Nema navedene opreme.</p>
        </section>

        <section class="details-section">
          <h3>Dodatne usluge</h3>

          <div
            v-if="selectedSpace.services?.length"
            class="services-list"
          >
            <article
              v-for="service in selectedSpace.services"
              :key="service.id || service.name"
              class="service-card"
            >
              <div>
                <strong>{{ service.name }}</strong>
                <p v-if="service.description">
                  {{ service.description }}
                </p>
              </div>

              <span>
                {{ formatPrice(service.price) }} KM
              </span>

              <small v-if="service.conditions">
                {{ service.conditions }}
              </small>
            </article>
          </div>

          <p v-else>Nema dodatnih usluga.</p>
        </section>

        <section
          v-if="selectedSpace.images?.length > 1"
          class="details-section"
        >
          <h3>Galerija</h3>

          <div class="details-gallery">
            <img
              v-for="image in selectedSpace.images"
              :key="image.id || image.url"
              :src="getImageUrl(image.url)"
              :alt="selectedSpace.name"
              @error="handleImageError"
            />
          </div>
        </section>
      </div>
    </div>
  </div>
</Teleport>
<SpaceCreateModal
  :is-open="isCreateModalOpen"
  @close="closeCreateSpace"
  @created="handleSpaceCreated"
/>
</template>