<script setup>
import { computed, ref } from 'vue'
import {
  createSpace,
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

const selectedFiles = ref([])
const primaryImageIndex = ref(0)
const newEquipmentName = ref('')

function getInitialForm() {
  return {
    name: '',
    description: '',
    space_type: '',
    space_subtype: '',
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

const subtypeOptions = computed(() => {
  const options = {
    office_workspace: [
      {
        value: 'private_office',
        label: 'Privatni ured',
      },
      {
        value: 'permanent_workspace',
        label: 'Stalno radno mjesto',
      },
      {
        value: 'flexible_package',
        label: 'Fleksibilni paket',
      },
      {
        value: 'virtual_office',
        label: 'Virtualni ured',
      },
    ],

    conference: [
      {
        value: 'meeting_room',
        label: 'Sala za sastanke',
      },
      {
        value: 'conference_hall',
        label: 'Konferencijska dvorana',
      },
    ],

    outdoor: [
      {
        value: 'terrace',
        label: 'Terasa',
      },
      {
        value: 'green_park',
        label: 'Zeleni park',
      },
    ],
  }

  return options[form.value.space_type] || []
})

function handleSpaceTypeChange() {
  form.value.space_subtype = ''

  if (form.value.space_type !== 'conference') {
    form.value.is_modular = false
    form.value.combination_group = null
  }
}

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
    !form.value.space_type ||
    !form.value.space_subtype
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


      space_type: form.value.space_type,
      space_subtype: form.value.space_subtype,

      capacity: Number(form.value.capacity),
      price: Number(form.value.price),
      price_unit: form.value.price_unit,

      is_modular:
        form.value.space_type === 'conference'
          ? form.value.is_modular
          : false,

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

        errorMessage.value =
          'Prostor je kreiran, ali slike nisu spremljene.'

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

    errorMessage.value =
      typeof detail === 'string'
        ? detail
        : 'Nije moguće kreirati prostor.'
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
                  <span>Glavna kategorija *</span>

                  <select
                    v-model="form.space_type"
                    required
                    @change="handleSpaceTypeChange"
                  >
                    <option value="" disabled>
                      Odaberite kategoriju
                    </option>

                    <option value="office_workspace">
                      Uredi i radni prostori
                    </option>

                    <option value="conference">
                      Konferencijske dvorane
                    </option>

                    <option value="outdoor">
                      Vanjski prostori
                    </option>
                  </select>
                </label>

                <label class="form-field">
                  <span>Podvrsta *</span>

                  <select
                    v-model="form.space_subtype"
                    required
                    :disabled="!form.space_type"
                  >
                    <option value="" disabled>
                      Odaberite podvrstu
                    </option>

                    <option
                      v-for="option in subtypeOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
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
                    <option value="hour">Po satu</option>
                    <option value="day">Po danu</option>
                    <option value="month">Mjesečno</option>

                    <option value="reservation">
                      Po rezervaciji
                    </option>
                  </select>
                </label>
              </div>

              <label
                v-if="form.space_type === 'conference'"
                class="checkbox-field"
              >
                <input
                  v-model="form.is_modular"
                  type="checkbox"
                />

                <span>
                  Modularna konferencijska dvorana
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

                  <span>{{ file.name }}</span>

                  <small>
                    {{
                      (file.size / 1024 / 1024)
                        .toFixed(2)
                    }}
                    MB
                  </small>
                </label>
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
              :disabled="isSaving"
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