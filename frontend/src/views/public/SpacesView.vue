<script setup>
import { computed, onMounted, ref } from 'vue'
import PublicSpaceCard from '../../components/public/PublicSpaceCard.vue'
import { getPublicSpaces } from '../../services/public/publicSpaceService'
import { publicCategories } from '../../data/publicSpaces'

const spaces = ref([])
const loading = ref(true)
const loadError = ref('')

const search = ref('')
const category = ref('Sve')
const capacity = ref(null)

function normalizeText(value) {
  return String(value ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
}

const filteredSpaces = computed(() => {
  const query = normalizeText(search.value)
  const minimumCapacity = Number(capacity.value) || 0

  return spaces.value.filter((space) => {
    const searchableContent = normalizeText([
      space.name,
      space.category,
      space.location,
      space.shortDescription,
      space.description,
      ...(space.equipment ?? []),
    ].join(' '))

    const matchesSearch =
      !query || searchableContent.includes(query)

    const matchesCategory =
      category.value === 'Sve' ||
      space.category === category.value

    const matchesCapacity =
      !minimumCapacity ||
      space.capacity >= minimumCapacity

    return (
      matchesSearch &&
      matchesCategory &&
      matchesCapacity
    )
  })
})

const hasActiveFilters = computed(() => {
  return Boolean(
    normalizeText(search.value) ||
    category.value !== 'Sve' ||
    Number(capacity.value) > 0
  )
})

function resetFilters() {
  search.value = ''
  category.value = 'Sve'
  capacity.value = null
}

async function loadSpaces() {
  loading.value = true
  loadError.value = ''

  try {
    spaces.value = await getPublicSpaces()
  } catch (error) {
    console.error('Greška pri učitavanju prostora:', error)
    loadError.value =
      'Prostore trenutno nije moguće učitati. Pokušajte ponovno.'
  } finally {
    loading.value = false
  }
}

onMounted(loadSpaces)
</script>

<template>
  <section class="public-section">
    <div class="public-container">
      <div class="public-page-heading">
        <span class="public-eyebrow">
          PONUDA PROSTORA
        </span>

        <h1>Pronađite odgovarajući prostor</h1>

        <p>
          Pretražite prostore prema nazivu, opisu,
          lokaciji, opremi, vrsti i potrebnom kapacitetu.
        </p>
      </div>

      <div class="public-filters">
        <v-text-field
          v-model="search"
          label="Pretražite prostore"
          placeholder="Naziv, lokacija, oprema..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          clearable
          hide-details
        />

        <v-select
          v-model="category"
          :items="publicCategories"
          label="Vrsta prostora"
          prepend-inner-icon="mdi-shape-outline"
          variant="outlined"
          hide-details
        />

        <v-text-field
          v-model.number="capacity"
          type="number"
          min="1"
          label="Minimalni kapacitet"
          prepend-inner-icon="mdi-account-group-outline"
          variant="outlined"
          clearable
          hide-details
        />
      </div>

      <div
        v-if="!loading && !loadError"
        class="public-results-toolbar"
        aria-live="polite"
      >
        <span>
          Pronađeno:
          <strong>{{ filteredSpaces.length }}</strong>

          {{
            filteredSpaces.length === 1
              ? 'prostor'
              : 'prostora'
          }}
        </span>

        <v-btn
          v-if="hasActiveFilters"
          variant="text"
          prepend-icon="mdi-filter-remove-outline"
          @click="resetFilters"
        >
          Očisti filtere
        </v-btn>
      </div>

      <v-alert
        v-if="loadError"
        type="error"
        variant="tonal"
        class="public-page-alert"
      >
        {{ loadError }}

        <template #append>
          <v-btn
            variant="text"
            @click="loadSpaces"
          >
            Pokušaj ponovno
          </v-btn>
        </template>
      </v-alert>

      <div
        v-else-if="loading"
        class="public-card-grid"
      >
        <v-skeleton-loader
          v-for="number in 6"
          :key="number"
          type="image, article, actions"
        />
      </div>

      <div
        v-else-if="filteredSpaces.length"
        class="public-card-grid"
      >
        <PublicSpaceCard
          v-for="space in filteredSpaces"
          :key="space.id"
          :space="space"
        />
      </div>

      <div
        v-else
        class="public-empty-state"
      >
        <v-icon
          icon="mdi-magnify-close"
          size="54"
        />

        <h2>Nema pronađenih prostora</h2>

        <p>
          Pokušajte upisati drugi pojam ili
          promijeniti odabrane filtere.
        </p>

        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-refresh"
          @click="resetFilters"
        >
          Poništi filtere
        </v-btn>
      </div>
    </div>
  </section>
</template>