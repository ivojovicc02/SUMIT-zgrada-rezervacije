<script setup>
import {
  fallbackSpaceImage,
  formatPrice,
  formatSpacePriceUnit,
  getPrimarySpaceImage,
  getSpaceImageUrl,
} from '../../utils/spaceFormatters'

defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },

  space: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close'])

const workingDays = [
  {
    key: 'monday',
    label: 'Ponedjeljak',
  },
  {
    key: 'tuesday',
    label: 'Utorak',
  },
  {
    key: 'wednesday',
    label: 'Srijeda',
  },
  {
    key: 'thursday',
    label: 'Četvrtak',
  },
  {
    key: 'friday',
    label: 'Petak',
  },
  {
    key: 'saturday',
    label: 'Subota',
  },
  {
    key: 'sunday',
    label: 'Nedjelja',
  },
]

function getWorkingDay(space, dayKey) {
  return space?.working_hours?.[dayKey] || null
}

function closeModal() {
  emit('close')
}

function handleImageError(event) {
  if (event.target.src !== fallbackSpaceImage) {
    event.target.src = fallbackSpaceImage
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen && space"
      class="modal-overlay"
      @click.self="closeModal"
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
                {{ space.name }}
              </h2>

              <span
                v-if="space.is_modular"
                class="modular-badge"
              >
                Modularna
              </span>
            </div>

            <p>
              {{
                space.subcategory?.name ||
                'Podkategorija nije definirana'
              }}
            </p>
          </div>

          <button
            class="modal-close-button"
            type="button"
            aria-label="Zatvori"
            @click="closeModal"
          >
            ×
          </button>
        </header>

        <div class="modal-content">
          <img
            class="details-main-image"
            :src="getPrimarySpaceImage(space)"
            :alt="space.name"
            @error="handleImageError"
          />

          <section class="details-section">
            <h3>Opis</h3>

            <p>
              {{ space.description }}
            </p>
          </section>

          <div class="details-grid">
            <div class="detail-item">
              <span>Glavna kategorija</span>

              <strong>
                {{
                  space.subcategory?.category?.name ||
                  'Nije definirano'
                }}
              </strong>
            </div>

            <div class="detail-item">
              <span>Podkategorija</span>

              <strong>
                {{
                  space.subcategory?.name ||
                  'Nije definirano'
                }}
              </strong>
            </div>

            <div class="detail-item">
              <span>Kapacitet</span>

              <strong>
                {{ space.capacity }} osoba
              </strong>
            </div>

            <div class="detail-item">
              <span>Cijena</span>

              <strong>
                {{ formatPrice(space.price) }} KM
                {{ formatSpacePriceUnit(space.price_unit) }}
              </strong>
            </div>
          </div>

          <section class="details-section">
            <h3>Oprema</h3>

            <div
              v-if="space.equipment?.length"
              class="details-tags"
            >
              <span
                v-for="equipment in space.equipment"
                :key="equipment.id || equipment.name"
                class="equipment-badge"
              >
                {{ equipment.name }}
              </span>
            </div>

            <p v-else>
              Nema navedene opreme.
            </p>
          </section>

          <section class="details-section">
            <h3>Dodatne usluge</h3>

            <div
              v-if="space.services?.length"
              class="services-list"
            >
              <article
                v-for="service in space.services"
                :key="service.id || service.name"
                class="service-card"
              >
                <div>
                  <strong>
                    {{ service.name }}
                  </strong>

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

            <p v-else>
              Nema dodatnih usluga.
            </p>
          </section>

          <section
            v-if="space.images?.length > 1"
            class="details-section"
          >
            <h3>Galerija</h3>

            <div class="details-gallery">
              <img
                v-for="image in space.images"
                :key="image.id || image.url"
                :src="getSpaceImageUrl(image.url)"
                :alt="space.name"
                @error="handleImageError"
              />
            </div>
          </section>
        </div>
      </div>
    </div>
  </Teleport>
</template>