<script setup>
import {
  onMounted,
  ref,
} from 'vue'

import {
  createSpace,
  getSpaceCategories,
  getSpaceSubcategories,
  uploadSpaceImages,
} from '../../services/admin/spaceService'

defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits([
  'close',
  'created',
])

const isSaving = ref(false)
const errorMessage = ref('')

const categories = ref([])
const subcategories = ref([])

const isLoadingCategories = ref(false)
const isLoadingSubcategories = ref(false)

const selectedFiles = ref([])
const primaryImageIndex = ref(0)
const newEquipmentName = ref('')

function getInitialForm() {
  return {
    name: '',
    description: '',
    category_id: '',
    subcategory_id: '',
    capacity: 1,
    price: 0,
    price_unit: 'hour',
    is_modular: false,
    combination_group: null,
    equipment: [],
    services: [],
  }
}

const form = ref(getInitialForm())

async function fetchCategories() {
  isLoadingCategories.value = true
  errorMessage.value = ''

  try {
    const response = await getSpaceCategories()

    categories.value = Array.isArray(response.data)
      ? response.data
      : []
  } catch (error) {
    console.error(
      'Greška pri dohvatu kategorija:',
      error,
    )

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće dohvatiti kategorije.'
  } finally {
    isLoadingCategories.value = false
  }
}

async function handleCategoryChange() {
  form.value.subcategory_id = ''
  subcategories.value = []

  if (!form.value.category_id) {
    return
  }

  isLoadingSubcategories.value = true
  errorMessage.value = ''

  try {
    const response = await getSpaceSubcategories({
      category_id: Number(form.value.category_id),
    })

    subcategories.value = Array.isArray(response.data)
      ? response.data
      : []
  } catch (error) {
    console.error(
      'Greška pri dohvatu podkategorija:',
      error,
    )

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće dohvatiti podkategorije.'
  } finally {
    isLoadingSubcategories.value = false
  }
}

onMounted(fetchCategories)

function addEquipment() {
  const name = newEquipmentName.value.trim()

  if (!name) {
    return
  }

  const exists = form.value.equipment.some(
    (equipment) =>
      equipment.name.toLowerCase() ===
      name.toLowerCase(),
  )

  if (exists) {
    return
  }

  form.value.equipment.push({ name })
  newEquipmentName.value = ''
}

function removeEquipment(index) {
  form.value.equipment.splice(index, 1)
}

function handleFilesSelected(event) {
  const files = Array.from(
    event.target.files || [],
  )

  selectedFiles.value = files
  primaryImageIndex.value = 0
}

function resetForm() {
  form.value = getInitialForm()

  subcategories.value = []
  selectedFiles.value = []
  primaryImageIndex.value = 0
  newEquipmentName.value = ''
  errorMessage.value = ''
}

function closeModal() {
  if (isSaving.value) {
    return
  }

  resetForm()
  emit('close')
}

async function submitForm() {
  errorMessage.value = ''

  if (
    !form.value.name.trim() ||
    !form.value.description.trim() ||
    !form.value.category_id ||
    !form.value.subcategory_id
  ) {
    errorMessage.value =
      'Popunite sva obavezna polja.'

    return
  }

  isSaving.value = true

  try {
    const payload = {
      name: form.value.name.trim(),
      description: form.value.description.trim(),

      subcategory_id: Number(
        form.value.subcategory_id,
      ),

      capacity: Number(form.value.capacity),
      price: Number(form.value.price),
      price_unit: form.value.price_unit,

      is_modular: form.value.is_modular,

      combination_group:
        form.value.is_modular
          ? form.value.combination_group || null
          : null,

      images: [],

      equipment: form.value.equipment.map(
        (equipment) => ({
          name: equipment.name,
        }),
      ),

      services: form.value.services,
    }

    const response = await createSpace(payload)
    const createdSpace = response.data

    if (!createdSpace?.id) {
      throw new Error(
        'Backend nije vratio ID kreiranog prostora.',
      )
    }

    if (selectedFiles.value.length > 0) {
      try {
        await uploadSpaceImages(
          createdSpace.id,
          selectedFiles.value,
          primaryImageIndex.value,
        )
      } catch (uploadError) {
        console.error(
          'Prostor je kreiran, ali slike nisu spremljene:',
          uploadError,
        )

        const detail =
          uploadError.response?.data?.detail

        errorMessage.value =
          typeof detail === 'string'
            ? `Prostor je kreiran, ali slike nisu spremljene: ${detail}`
            : 'Prostor je kreiran, ali slike nisu spremljene.'

        emit('created', createdSpace)
        return
      }
    }

    emit('created', createdSpace)
    resetForm()
    emit('close')
  } catch (error) {
    console.error(
      'Greška pri kreiranju prostora:',
      error,
    )

    const detail = error.response?.data?.detail

    if (typeof detail === 'string') {
      errorMessage.value = detail
    } else if (Array.isArray(detail)) {
      errorMessage.value =
        detail
          .map((item) => item.msg)
          .join(', ') ||
        'Podaci forme nisu ispravni.'
    } else {
      errorMessage.value =
        'Nije moguće kreirati prostor.'
    }
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="modal-overlay"
      @click.self="closeModal"
    >
      <div
        class="space-create-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-space-title"
      >
        <header class="modal-header">
          <div>
            <h2 id="create-space-title">
              Dodaj novi prostor
            </h2>

            <p>
              Unesite osnovne podatke, opremu i slike
              prostora.
            </p>
          </div>

          <button
            class="modal-close-button"
            type="button"
            aria-label="Zatvori"
            :disabled="isSaving"
            @click="closeModal"
          >
            ×
          </button>
        </header>

        <form
          class="create-space-form"
          @submit.prevent="submitForm"
        >
          <div class="create-modal-content">
            <section class="form-section">
              <h3>Osnovni podaci</h3>

              <div class="form-grid">
                <label class="form-field">
                  <span>Naziv *</span>

                  <input
                    v-model="form.name"
                    type="text"
                    maxlength="100"
                    required
                  />
                </label>

                <label
                  class="form-field form-field--full"
                >
                  <span>Opis *</span>

                  <textarea
                    v-model="form.description"
                    rows="4"
                    required
                  ></textarea>
                </label>
              </div>
            </section>

            <section class="form-section">
              <h3>Vrsta i cijena</h3>

              <div class="form-grid">
                <label class="form-field">
                  <span>Kategorija *</span>

                  <select
                    v-model="form.category_id"
                    required
                    :disabled="isLoadingCategories"
                    @change="handleCategoryChange"
                  >
                    <option value="" disabled>
                      {{
                        isLoadingCategories
                          ? 'Učitavanje kategorija...'
                          : 'Odaberite kategoriju'
                      }}
                    </option>

                    <option
                      v-for="category in categories"
                      :key="category.id"
                      :value="category.id"
                    >
                      {{ category.name }}
                    </option>
                  </select>
                </label>

                <label class="form-field">
                  <span>Podkategorija *</span>

                  <select
                    v-model="form.subcategory_id"
                    required
                    :disabled="
                      !form.category_id ||
                      isLoadingSubcategories
                    "
                  >
                    <option value="" disabled>
                      {{
                        isLoadingSubcategories
                          ? 'Učitavanje podkategorija...'
                          : 'Odaberite podkategoriju'
                      }}
                    </option>

                    <option
                      v-for="subcategory in subcategories"
                      :key="subcategory.id"
                      :value="subcategory.id"
                    >
                      {{ subcategory.name }}
                    </option>
                  </select>
                </label>

                <label class="form-field">
                  <span>Kapacitet *</span>

                  <input
                    v-model.number="form.capacity"
                    type="number"
                    min="1"
                    required
                  />
                </label>

                <label class="form-field">
                  <span>Cijena *</span>

                  <input
                    v-model.number="form.price"
                    type="number"
                    min="0"
                    step="0.01"
                    required
                  />
                </label>

                <label class="form-field">
                  <span>Jedinica naplate *</span>

                  <select
                    v-model="form.price_unit"
                    required
                  >
                    <option value="hour">
                      Po satu
                    </option>

                    <option value="day">
                      Po danu
                    </option>

                    <option value="month">
                      Mjesečno
                    </option>

                    <option value="reservation">
                      Po rezervaciji
                    </option>
                  </select>
                </label>
              </div>

              <label class="checkbox-field">
                <input
                  v-model="form.is_modular"
                  type="checkbox"
                />

                <span>
                  Modularni/povezivi prostor
                </span>
              </label>
            </section>

            <section class="form-section">
              <h3>Oprema</h3>

              <div class="equipment-input-row">
                <input
                  v-model="newEquipmentName"
                  type="text"
                  placeholder="Primjer: Projektor"
                  @keydown.enter.prevent="addEquipment"
                />

                <button
                  type="button"
                  class="secondary-button"
                  @click="addEquipment"
                >
                  Dodaj
                </button>
              </div>

              <div
                v-if="form.equipment.length"
                class="selected-equipment-list"
              >
                <span
                  v-for="(equipment, index) in form.equipment"
                  :key="`${equipment.name}-${index}`"
                  class="selected-equipment-item"
                >
                  {{ equipment.name }}

                  <button
                    type="button"
                    aria-label="Ukloni opremu"
                    @click="removeEquipment(index)"
                  >
                    ×
                  </button>
                </span>
              </div>

              <p
                v-else
                class="form-help-text"
              >
                Oprema nije obavezna.
              </p>
            </section>

            <section class="form-section">
              <h3>Slike</h3>

              <label class="file-upload-field">
                <span>
                  Odaberite JPG, PNG ili WEBP slike
                </span>

                <input
                  type="file"
                  accept=".jpg,.jpeg,.png,.webp"
                  multiple
                  @change="handleFilesSelected"
                />
              </label>

              <div
                v-if="selectedFiles.length"
                class="selected-files-list"
              >
                <label
                  v-for="(file, index) in selectedFiles"
                  :key="`${file.name}-${index}`"
                  class="selected-file-item"
                >
                  <input
                    v-model.number="primaryImageIndex"
                    type="radio"
                    name="primary-image"
                    :value="index"
                  />

                  <span>
                    {{ file.name }}
                  </span>

                  <small>
                    {{
                      (
                        file.size /
                        1024 /
                        1024
                      ).toFixed(2)
                    }}
                    MB
                  </small>
                </label>

                <p class="form-help-text">
                  Označena slika bit će glavna.
                </p>
              </div>
            </section>

            <p
              v-if="errorMessage"
              class="create-form-error"
            >
              {{ errorMessage }}
            </p>
          </div>

          <footer class="create-modal-footer">
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
              :disabled="
                isSaving ||
                isLoadingCategories ||
                isLoadingSubcategories
              "
            >
              {{
                isSaving
                  ? 'Spremanje...'
                  : 'Spremi prostor'
              }}
            </button>
          </footer>
        </form>
      </div>
    </div>
  </Teleport>
</template>