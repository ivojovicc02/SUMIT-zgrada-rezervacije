<script setup>
import {
  computed,
  onUnmounted,
  reactive,
  ref,
  watch,
} from 'vue'

import {
  deleteSpaceImage,
  getSpaceCategories,
  setPrimarySpaceImage,
  updateSpaceById,
  uploadSpaceImages,
  getSpaceSubcategories,
} from '../../services/admin/spaceService'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },

  space: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits([
  'close',
  'updated',
])

const days = [
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

function createDefaultWorkingHours() {
  return {
    monday: {
      is_closed: false,
      opens_at: '08:00',
      closes_at: '16:00',
    },
    tuesday: {
      is_closed: false,
      opens_at: '08:00',
      closes_at: '16:00',
    },
    wednesday: {
      is_closed: false,
      opens_at: '08:00',
      closes_at: '16:00',
    },
    thursday: {
      is_closed: false,
      opens_at: '08:00',
      closes_at: '16:00',
    },
    friday: {
      is_closed: false,
      opens_at: '08:00',
      closes_at: '16:00',
    },
    saturday: {
      is_closed: true,
      opens_at: null,
      closes_at: null,
    },
    sunday: {
      is_closed: true,
      opens_at: null,
      closes_at: null,
    },
  }
}

const form = reactive({
  name: '',
  description: '',
  subcategory_id: '',
  capacity: 1,
  price: 0,
  price_unit: 'hour',
  is_modular: false,
  combination_group: '',
  equipment: [],
  services: [],
  working_hours: createDefaultWorkingHours(),
})

const categories = ref([])
const currentImages = ref([])
const newImages = ref([])
const newImagePreviews = ref([])

const isLoadingCategories = ref(false)
const isSaving = ref(false)
const uploadingImages = ref(false)
const deletingImageId = ref(null)
const settingPrimaryImageId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')

const fileInput = ref(null)

const selectedCategoryId = ref('')
const subcategories = ref([])
const availableSubcategories = computed(() => {
    
  if (!selectedCategoryId.value) {
    return []
  }

  const category = categories.value.find(
    (item) => Number(item.id) ===
      Number(selectedCategoryId.value),
  )

  return Array.isArray(category?.subcategories)
    ? category.subcategories
    : []
})

const selectedSubcategory = computed(() => {
  for (const category of categories.value) {
    const subcategory = category.subcategories?.find(
      (item) => Number(item.id) ===
        Number(form.subcategory_id),
    )

    if (subcategory) {
      return subcategory
    }
  }

  return null
})

function getEmptyEquipmentItem() {
  return {
    name: '',
  }
}

function getEmptyServiceItem() {
  return {
    name: '',
    price: 0,
  }
}

function normalizeWorkingHours(workingHours) {
  const defaults = createDefaultWorkingHours()

  if (!workingHours || typeof workingHours !== 'object') {
    return defaults
  }

  const normalized = {}

  for (const day of days) {
    const existingDay = workingHours[day.key]

    normalized[day.key] = {
      is_closed:
        existingDay?.is_closed ??
        existingDay?.closed ??
        defaults[day.key].is_closed,

      opens_at:
        existingDay?.opens_at ??
        defaults[day.key].opens_at,

      closes_at:
        existingDay?.closes_at ??
        defaults[day.key].closes_at,
    }
  }

  return normalized
}

function populateForm(space) {
  form.name = space?.name || ''
  form.description = space?.description || ''
  form.subcategory_id =
    space?.subcategory_id ||
    space?.subcategory?.id ||
    ''

  form.capacity = Number(space?.capacity || 1)
  form.price = Number(space?.price || 0)
  form.price_unit = space?.price_unit || 'hour'
  form.is_modular = Boolean(space?.is_modular)
  form.combination_group = space?.combination_group || ''

  form.equipment = Array.isArray(space?.equipment)
    ? space.equipment.map((item) => ({
        name: item?.name || '',
      }))
    : []

  form.services = Array.isArray(space?.services)
    ? space.services.map((service) => ({
        name: service?.name || '',
        price: Number(service?.price || 0),
      }))
    : []

  form.working_hours = normalizeWorkingHours(
    space?.working_hours,
  )

  currentImages.value = Array.isArray(space?.images)
    ? space.images.map((image) => ({
        ...image,
      }))
    : []

  const categoryId =
    space?.subcategory?.category?.id ||
    space?.category_id ||
    ''

  selectedCategoryId.value = categoryId
}

async function fetchCategories() {
  isLoadingCategories.value = true

  try {
    const response = await getSpaceCategories()

    categories.value = Array.isArray(response.data)
      ? response.data
      : []
  } catch (error) {
    console.error(
      'Greška pri dohvaćanju kategorija:',
      error,
    )

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće dohvatiti kategorije prostora.'
  } finally {
    isLoadingCategories.value = false
  }
}

async function initializeModal() {
  errorMessage.value = ''
  successMessage.value = ''

  clearNewImages()

  await fetchCategories()

  if (props.space) {
    populateForm(props.space)

    if (
      !selectedCategoryId.value &&
      selectedSubcategory.value
    ) {
      selectedCategoryId.value =
        selectedSubcategory.value.category_id ||
        ''
    }
  }
}

watch(
  () => props.isOpen,
  async (isOpen) => {
    document.body.style.overflow = isOpen
      ? 'hidden'
      : ''

    if (isOpen && props.space) {
      await initializeModal()
    }
  },
)

watch(
  () => props.space,
  (space) => {
    if (props.isOpen && space) {
      populateForm(space)
    }
  },
)

watch(selectedCategoryId, (newCategoryId, oldCategoryId) => {
  if (
    oldCategoryId &&
    Number(newCategoryId) !== Number(oldCategoryId)
  ) {
    const subcategoryStillExists =
      availableSubcategories.value.some(
        (item) =>
          Number(item.id) ===
          Number(form.subcategory_id),
      )

    if (!subcategoryStillExists) {
      form.subcategory_id = ''
    }
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
  revokePreviewUrls()
})

function closeModal() {
  if (
    isSaving.value ||
    uploadingImages.value ||
    deletingImageId.value !== null
  ) {
    return
  }

  clearNewImages()
  errorMessage.value = ''
  successMessage.value = ''

  emit('close')
}

function handleBackdropClick(event) {
  if (event.target === event.currentTarget) {
    closeModal()
  }
}

function addEquipment() {
  form.equipment.push(getEmptyEquipmentItem())
}

function removeEquipment(index) {
  form.equipment.splice(index, 1)
}

function addService() {
  form.services.push(getEmptyServiceItem())
}

function removeService(index) {
  form.services.splice(index, 1)
}

function handleClosedDayChange(dayKey) {
  const day = form.working_hours[dayKey]

  if (day.is_closed) {
    day.opens_at = null
    day.closes_at = null
  } else {
    day.opens_at = '08:00'
    day.closes_at = '16:00'
  }
}

function revokePreviewUrls() {
  for (const preview of newImagePreviews.value) {
    URL.revokeObjectURL(preview.url)
  }
}

function clearNewImages() {
  revokePreviewUrls()

  newImages.value = []
  newImagePreviews.value = []

  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function handleNewImages(event) {
  errorMessage.value = ''

  const selectedFiles = Array.from(
    event.target.files || [],
  )

  if (!selectedFiles.length) {
    return
  }

  const totalImages =
    currentImages.value.length +
    newImages.value.length +
    selectedFiles.length

  if (totalImages > 10) {
    errorMessage.value =
      'Prostor može imati najviše 10 slika.'

    event.target.value = ''
    return
  }

  const allowedTypes = [
    'image/jpeg',
    'image/png',
    'image/webp',
  ]

  for (const file of selectedFiles) {
    if (!allowedTypes.includes(file.type)) {
      errorMessage.value =
        `Datoteka "${file.name}" nije podržana.`

      event.target.value = ''
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      errorMessage.value =
        `Datoteka "${file.name}" veća je od 5 MB.`

      event.target.value = ''
      return
    }
  }

  for (const file of selectedFiles) {
    newImages.value.push(file)

    newImagePreviews.value.push({
      file,
      name: file.name,
      url: URL.createObjectURL(file),
    })
  }

  event.target.value = ''
}

function removeNewImage(index) {
  const preview = newImagePreviews.value[index]

  if (preview?.url) {
    URL.revokeObjectURL(preview.url)
  }

  newImages.value.splice(index, 1)
  newImagePreviews.value.splice(index, 1)
}

function getImageUrl(url) {
  if (!url) {
    return ''
  }

  if (
    url.startsWith('http://') ||
    url.startsWith('https://')
  ) {
    return url
  }

  const apiUrl =
    import.meta.env.VITE_API_URL ||
    'http://localhost:8000'

  return `${apiUrl}${url}`
}

function validateForm() {
  if (!form.name.trim()) {
    return 'Naziv prostora je obavezan.'
  }

  if (!form.subcategory_id) {
    return 'Odaberite podkategoriju prostora.'
  }

  if (
    !Number.isInteger(Number(form.capacity)) ||
    Number(form.capacity) < 1
  ) {
    return 'Kapacitet mora biti najmanje 1.'
  }

  if (
    Number.isNaN(Number(form.price)) ||
    Number(form.price) < 0
  ) {
    return 'Cijena ne može biti negativna.'
  }

  for (const day of days) {
    const workingDay = form.working_hours[day.key]

    if (workingDay.is_closed) {
      continue
    }

    if (
      !workingDay.opens_at ||
      !workingDay.closes_at
    ) {
      return (
        `Unesite radno vrijeme za: ` +
        `${day.label}.`
      )
    }

    if (
      workingDay.opens_at >=
      workingDay.closes_at
    ) {
      return (
        `Vrijeme otvaranja mora biti prije ` +
        `zatvaranja za: ${day.label}.`
      )
    }
  }

  return null
}

function buildUpdatePayload() {
  const workingHours = {}

  for (const day of days) {
    const value = form.working_hours[day.key]

    workingHours[day.key] = {
      is_closed: Boolean(value.is_closed),
      opens_at: value.is_closed
        ? null
        : value.opens_at,
      closes_at: value.is_closed
        ? null
        : value.closes_at,
    }
  }

  return {
    name: form.name.trim(),
    description: form.description.trim() || null,
    subcategory_id: Number(form.subcategory_id),
    capacity: Number(form.capacity),
    price: Number(form.price),
    price_unit: form.price_unit,
    is_modular: Boolean(form.is_modular),
    combination_group:
      form.is_modular &&
      form.combination_group.trim()
        ? form.combination_group.trim()
        : null,

    equipment: form.equipment
      .map((item) => ({
        name: item.name.trim(),
      }))
      .filter((item) => item.name),

    services: form.services
      .map((service) => ({
        name: service.name.trim(),
        price: Number(service.price || 0),
      }))
      .filter((service) => service.name),

    working_hours: workingHours,
  }
}

async function submitForm() {
  if (!props.space?.id) {
    return
  }

  errorMessage.value = ''
  successMessage.value = ''

  const validationError = validateForm()

  if (validationError) {
    errorMessage.value = validationError
    return
  }

  isSaving.value = true

  try {
    const payload = buildUpdatePayload()

    await updateSpaceById(
      props.space.id,
      payload,
    )

    if (newImages.value.length > 0) {
      uploadingImages.value = true

      try {
        await uploadSpaceImages(
          props.space.id,
          newImages.value,
        )
      } finally {
        uploadingImages.value = false
      }
    }

    successMessage.value =
      'Prostor je uspješno ažuriran.'

    clearNewImages()

    emit('updated')
  } catch (error) {
    console.error(
      'Greška pri uređivanju prostora:',
      error,
    )

    const detail = error.response?.data?.detail

    errorMessage.value =
      typeof detail === 'string'
        ? detail
        : 'Nije moguće spremiti promjene.'
  } finally {
    isSaving.value = false
  }
}

async function makePrimary(image) {
  if (
    !props.space?.id ||
    !image?.id ||
    image.is_primary
  ) {
    return
  }

  errorMessage.value = ''
  successMessage.value = ''
  settingPrimaryImageId.value = image.id

  try {
    await setPrimarySpaceImage(
      props.space.id,
      image.id,
    )

    currentImages.value =
      currentImages.value.map((item) => ({
        ...item,
        is_primary: item.id === image.id,
      }))

    successMessage.value =
      'Glavna slika je uspješno promijenjena.'

    emit('updated')
  } catch (error) {
    console.error(
      'Greška pri promjeni glavne slike:',
      error,
    )

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće promijeniti glavnu sliku.'
  } finally {
    settingPrimaryImageId.value = null
  }
}

async function removeExistingImage(image) {
  if (!props.space?.id || !image?.id) {
    return
  }

  const confirmed = window.confirm(
    'Jeste li sigurni da želite obrisati ovu sliku?',
  )

  if (!confirmed) {
    return
  }

  errorMessage.value = ''
  successMessage.value = ''
  deletingImageId.value = image.id

  try {
    const response = await deleteSpaceImage(
      props.space.id,
      image.id,
    )

    currentImages.value =
      currentImages.value.filter(
        (item) => item.id !== image.id,
      )

    const newPrimary =
      response.data?.new_primary_image

    if (newPrimary) {
      currentImages.value =
        currentImages.value.map((item) => ({
          ...item,
          is_primary: item.id === newPrimary.id,
        }))
    }

    successMessage.value =
      'Slika je uspješno obrisana.'

    emit('updated')
  } catch (error) {
    console.error(
      'Greška pri brisanju slike:',
      error,
    )

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće obrisati sliku.'
  } finally {
    deletingImageId.value = null
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen && space"
      class="modal-backdrop"
      @click="handleBackdropClick"
    >
      <div
        class="space-edit-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-space-title"
      >
        <header class="modal-header">
          <div>
            <h2 id="edit-space-title">
              Uredi prostor
            </h2>

            <p>
              Uređujete prostor:
              <strong>{{ space.name }}</strong>
            </p>
          </div>

          <button
            type="button"
            class="modal-close-button"
            aria-label="Zatvori"
            :disabled="isSaving"
            @click="closeModal"
          >
            ×
          </button>
        </header>

        <form
          class="space-edit-form"
          @submit.prevent="submitForm"
        >
          <p
            v-if="errorMessage"
            class="form-message form-message--error"
          >
            {{ errorMessage }}
          </p>

          <p
            v-if="successMessage"
            class="form-message form-message--success"
          >
            {{ successMessage }}
          </p>

          <section class="form-section">
            <h3>Osnovni podaci</h3>

            <div class="form-grid">
              <div class="form-group form-group--full">
                <label for="edit-space-name">
                  Naziv prostora
                </label>

                <input
                  id="edit-space-name"
                  v-model.trim="form.name"
                  type="text"
                  maxlength="150"
                  required
                />
              </div>

              <div class="form-group">
                <label for="edit-category">
                  Kategorija
                </label>

                <select
                  id="edit-category"
                  v-model="selectedCategoryId"
                  :disabled="isLoadingCategories"
                >
                  <option value="">
                    Odaberite kategoriju
                  </option>

                  <option
                    v-for="category in categories"
                    :key="category.id"
                    :value="category.id"
                  >
                    {{ category.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="edit-subcategory">
                  Podkategorija
                </label>

                <select
                  id="edit-subcategory"
                  v-model="form.subcategory_id"
                  :disabled="
                    !selectedCategoryId ||
                    isLoadingCategories
                  "
                  required
                >
                  <option value="">
                    Odaberite podkategoriju
                  </option>

                  <option
                    v-for="subcategory in availableSubcategories"
                    :key="subcategory.id"
                    :value="subcategory.id"
                  >
                    {{ subcategory.name }}
                  </option>
                </select>
              </div>

              <div class="form-group form-group--full">
                <label for="edit-space-description">
                  Opis
                </label>

                <textarea
                  id="edit-space-description"
                  v-model="form.description"
                  maxlength="3000"
                  placeholder="Unesite opis prostora..."
                ></textarea>
              </div>

              <div class="form-group">
                <label for="edit-capacity">
                  Kapacitet
                </label>

                <input
                  id="edit-capacity"
                  v-model.number="form.capacity"
                  type="number"
                  min="1"
                  step="1"
                  required
                />
              </div>

              <div class="form-group">
                <label for="edit-price">
                  Cijena u KM
                </label>

                <input
                  id="edit-price"
                  v-model.number="form.price"
                  type="number"
                  min="0"
                  step="0.01"
                  required
                />
              </div>

              <div class="form-group">
                <label for="edit-price-unit">
                  Jedinica cijene
                </label>

                <select
                  id="edit-price-unit"
                  v-model="form.price_unit"
                  required
                >
                  <option value="hour">
                    Po satu
                  </option>

                  <option value="day">
                    Po danu
                  </option>

                  <option value="event">
                    Po događaju
                  </option>
                </select>
              </div>

              <div class="form-group checkbox-group">
                <label>
                  <input
                    v-model="form.is_modular"
                    type="checkbox"
                  />

                  Modularni prostor
                </label>
              </div>

              <div
                v-if="form.is_modular"
                class="form-group form-group--full"
              >
                <label for="edit-combination-group">
                  Grupa kombiniranja
                </label>

                <input
                  id="edit-combination-group"
                  v-model="form.combination_group"
                  type="text"
                  placeholder="Primjer: konferencijske-dvorane-a"
                />
              </div>
            </div>
          </section>

          <section class="form-section">
            <div class="section-heading">
              <h3>Oprema</h3>

              <button
                type="button"
                class="small-button"
                @click="addEquipment"
              >
                + Dodaj opremu
              </button>
            </div>

            <p
              v-if="form.equipment.length === 0"
              class="empty-text"
            >
              Nema unesene opreme.
            </p>

            <div
              v-for="(equipment, index) in form.equipment"
              :key="index"
              class="dynamic-row"
            >
              <input
                v-model="equipment.name"
                type="text"
                placeholder="Naziv opreme"
              />

              <button
                type="button"
                class="remove-button"
                aria-label="Ukloni opremu"
                @click="removeEquipment(index)"
              >
                ×
              </button>
            </div>
          </section>

          <section class="form-section">
            <div class="section-heading">
              <h3>Dodatne usluge</h3>

              <button
                type="button"
                class="small-button"
                @click="addService"
              >
                + Dodaj uslugu
              </button>
            </div>

            <p
              v-if="form.services.length === 0"
              class="empty-text"
            >
              Nema unesenih dodatnih usluga.
            </p>

            <div
              v-for="(service, index) in form.services"
              :key="index"
              class="dynamic-row dynamic-row--service"
            >
              <input
                v-model="service.name"
                type="text"
                placeholder="Naziv usluge"
              />

              <input
                v-model.number="service.price"
                type="number"
                min="0"
                step="0.01"
                placeholder="Cijena"
              />

              <button
                type="button"
                class="remove-button"
                aria-label="Ukloni uslugu"
                @click="removeService(index)"
              >
                ×
              </button>
            </div>
          </section>

          <section class="form-section">
            <h3>Radno vrijeme</h3>

            <div class="working-hours">
              <div
                v-for="day in days"
                :key="day.key"
                class="working-day"
              >
                <strong>{{ day.label }}</strong>

                <label class="closed-checkbox">
                  <input
                    v-model="
                      form.working_hours[day.key].is_closed
                    "
                    type="checkbox"
                    @change="
                      handleClosedDayChange(day.key)
                    "
                  />

                  Zatvoreno
                </label>

                <template
                  v-if="
                    !form.working_hours[day.key].is_closed
                  "
                >
                  <input
                    v-model="
                      form.working_hours[day.key].opens_at
                    "
                    type="time"
                  />

                  <span>–</span>

                  <input
                    v-model="
                      form.working_hours[day.key].closes_at
                    "
                    type="time"
                  />
                </template>
              </div>
            </div>
          </section>

          <section class="form-section">
            <div class="section-heading">
              <div>
                <h3>Galerija</h3>

                <p class="section-description">
                  Maksimalno 10 slika, do 5 MB po slici.
                </p>
              </div>
            </div>

            <div
              v-if="currentImages.length"
              class="image-grid"
            >
              <article
                v-for="image in currentImages"
                :key="image.id"
                class="image-card"
                :class="{
                  'image-card--primary': image.is_primary,
                }"
              >
                <div class="image-preview">
                  <img
                    :src="getImageUrl(image.url)"
                    :alt="`Slika prostora ${form.name}`"
                  />

                  <span
                    v-if="image.is_primary"
                    class="primary-badge"
                  >
                    Glavna
                  </span>
                </div>

                <div class="image-actions">
                  <button
                    v-if="!image.is_primary"
                    type="button"
                    class="image-action-button"
                    :disabled="
                      settingPrimaryImageId === image.id
                    "
                    @click="makePrimary(image)"
                  >
                    {{
                      settingPrimaryImageId === image.id
                        ? 'Postavljanje...'
                        : 'Postavi glavnu'
                    }}
                  </button>

                  <button
                    type="button"
                    class="image-action-button image-action-button--danger"
                    :disabled="
                      deletingImageId === image.id
                    "
                    @click="removeExistingImage(image)"
                  >
                    {{
                      deletingImageId === image.id
                        ? 'Brisanje...'
                        : 'Obriši'
                    }}
                  </button>
                </div>
              </article>
            </div>

            <p
              v-else
              class="empty-text"
            >
              Prostor trenutno nema slika.
            </p>

            <div class="upload-area">
              <label for="edit-space-images">
                Dodaj nove slike
              </label>

              <input
                id="edit-space-images"
                ref="fileInput"
                type="file"
                accept=".jpg,.jpeg,.png,.webp"
                multiple
                @change="handleNewImages"
              />
            </div>

            <div
              v-if="newImagePreviews.length"
              class="image-grid new-images-grid"
            >
              <article
                v-for="(preview, index) in newImagePreviews"
                :key="preview.url"
                class="image-card"
              >
                <div class="image-preview">
                  <img
                    :src="preview.url"
                    :alt="preview.name"
                  />

                  <span class="new-image-badge">
                    Nova
                  </span>
                </div>

                <button
                  type="button"
                  class="image-action-button image-action-button--danger"
                  @click="removeNewImage(index)"
                >
                  Ukloni
                </button>
              </article>
            </div>
          </section>

          <footer class="modal-footer">
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
              {{
                isSaving
                  ? 'Spremanje...'
                  : 'Spremi promjene'
              }}
            </button>
          </footer>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgb(15 23 42 / 60%);
}

.space-edit-modal {
  width: min(920px, 100%);
  max-height: 92vh;
  overflow-y: auto;
  border-radius: 16px;
  background: white;
  box-shadow: 0 24px 60px rgb(15 23 42 / 24%);
}

.modal-header {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
  background: white;
}

.modal-header h2,
.form-section h3 {
  margin: 0;
}

.modal-header p {
  margin: 6px 0 0;
  color: #64748b;
}

.modal-close-button {
  border: 0;
  background: transparent;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
}

.space-edit-form {
  padding: 24px;
}

.form-section {
  padding: 24px 0;
  border-bottom: 1px solid #e5e7eb;
}

.form-section:first-of-type {
  padding-top: 0;
}

.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-description {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 14px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-top: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group--full {
  grid-column: 1 / -1;
}

.form-group label,
.upload-area label {
  font-weight: 600;
}

.form-group input,
.form-group textarea,
.form-group select,
.dynamic-row input {
  width: 100%;
  box-sizing: border-box;
  padding: 11px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: white;
  font: inherit;
}

.form-group textarea {
  min-height: 110px;
  resize: vertical;
}

.checkbox-group {
  justify-content: flex-end;
}

.checkbox-group label,
.closed-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkbox-group input,
.closed-checkbox input {
  width: auto;
}

.dynamic-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  margin-top: 12px;
}

.dynamic-row--service {
  grid-template-columns: minmax(0, 1fr) 140px auto;
}

.remove-button {
  width: 42px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fff1f2;
  color: #be123c;
  font-size: 22px;
  cursor: pointer;
}

.small-button {
  padding: 8px 12px;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  background: #eff6ff;
  color: #1d4ed8;
  cursor: pointer;
}

.working-hours {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 18px;
}

.working-day {
  display: grid;
  grid-template-columns: 140px 120px 130px 20px 130px;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.working-day input[type='time'] {
  padding: 8px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(
    auto-fill,
    minmax(190px, 1fr)
  );
  gap: 16px;
  margin-top: 18px;
}

.image-card {
  overflow: hidden;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: white;
}

.image-card--primary {
  border: 2px solid #2563eb;
}

.image-preview {
  position: relative;
  height: 145px;
  background: #f1f5f9;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.primary-badge,
.new-image-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 5px 8px;
  border-radius: 999px;
  background: #2563eb;
  color: white;
  font-size: 12px;
  font-weight: 700;
}

.new-image-badge {
  background: #059669;
}

.image-actions {
  display: flex;
  gap: 8px;
  padding: 10px;
}

.image-action-button {
  flex: 1;
  padding: 8px;
  border: 1px solid #bfdbfe;
  border-radius: 7px;
  background: #eff6ff;
  color: #1d4ed8;
  cursor: pointer;
}

.image-action-button--danger {
  border-color: #fecaca;
  background: #fff1f2;
  color: #be123c;
}

.upload-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 22px;
  padding: 18px;
  border: 1px dashed #94a3b8;
  border-radius: 10px;
  background: #f8fafc;
}

.form-message {
  margin: 0 0 18px;
  padding: 12px 14px;
  border-radius: 8px;
}

.form-message--error {
  border: 1px solid #fecaca;
  background: #fff1f2;
  color: #be123c;
}

.form-message--success {
  border: 1px solid #bbf7d0;
  background: #f0fdf4;
  color: #15803d;
}

.empty-text {
  color: #64748b;
}

.modal-footer {
  position: sticky;
  bottom: 0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  background: white;
}

.secondary-button,
.primary-button {
  padding: 11px 18px;
  border-radius: 8px;
  font: inherit;
  cursor: pointer;
}

.secondary-button {
  border: 1px solid #cbd5e1;
  background: white;
}

.primary-button {
  border: 0;
  background: #2563eb;
  color: white;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 760px) {
  .modal-backdrop {
    padding: 10px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-group--full {
    grid-column: auto;
  }

  .working-day {
    grid-template-columns: 1fr 1fr;
  }

  .working-day strong {
    grid-column: 1 / -1;
  }

  .dynamic-row--service {
    grid-template-columns: 1fr;
  }

  .remove-button {
    width: 100%;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .modal-footer button {
    width: 100%;
  }
}
</style>