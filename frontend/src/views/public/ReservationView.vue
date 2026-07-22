<script setup>
import {
  computed,
  reactive,
  ref,
  watch,
} from 'vue'

import {
  useRoute,
  useRouter,
} from 'vue-router'

import { publicSpaces } from '../../data/publicSpaces'
import { createPublicReservation } from '../../services/public/publicReservationService'

const route = useRoute()
const router = useRouter()

const parsedSpaceId = Number(route.query.space)

const initialSpaceId =
  Number.isInteger(parsedSpaceId) &&
  publicSpaces.some((space) => space.id === parsedSpaceId)
    ? parsedSpaceId
    : null

const step = ref(1)
const loading = ref(false)
const validationMessage = ref('')
const submitError = ref('')

const stepLabels = [
  'Prostor',
  'Termin',
  'Podaci',
  'Opcije',
  'Pregled',
]

const extras = [
  {
    title: 'Catering',
    description: 'Priprema hrane i pića za sudionike.',
    price: 15,
  },
  {
    title: 'Tehnička podrška',
    description: 'Pomoć pri postavljanju i korištenju opreme.',
    price: 30,
  },
  {
    title: 'Dodatna oprema',
    description:
      'Dodatni monitori, mikrofoni ili prezentacijska oprema.',
    price: 20,
  },
  {
    title: 'Parking',
    description:
      'Rezervirano parkirno mjesto za vrijeme korištenja prostora.',
    price: 5,
  },
]

const form = reactive({
  spaceId: initialSpaceId,
  date: '',
  startTime: '',
  endTime: '',
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  company: '',
  eventName: '',
  note: '',
  guests: 1,
  extras: [],
})

const currentYear = new Date().getFullYear()

const dateParts = reactive({
  day: null,
  month: null,
  year: currentYear,
})

const startTimeParts = reactive({
  hour: null,
  minute: '00',
})

const endTimeParts = reactive({
  hour: null,
  minute: '00',
})

function padNumber(value) {
  return String(value).padStart(2, '0')
}

function toLocalISODate(date) {
  const timezoneOffset =
    date.getTimezoneOffset() * 60000

  return new Date(
    date.getTime() - timezoneOffset
  )
    .toISOString()
    .slice(0, 10)
}

const minimumDate = toLocalISODate(new Date())

const monthOptions = Array.from(
  { length: 12 },
  (_, index) => ({
    title: padNumber(index + 1),
    value: index + 1,
  })
)

const yearOptions = Array.from(
  { length: 6 },
  (_, index) => currentYear + index
)

const dayOptions = computed(() => {
  const selectedMonth = Number(dateParts.month)
  const selectedYear = Number(dateParts.year)

  const numberOfDays =
    selectedMonth && selectedYear
      ? new Date(
          selectedYear,
          selectedMonth,
          0
        ).getDate()
      : 31

  return Array.from(
    { length: numberOfDays },
    (_, index) => ({
      title: padNumber(index + 1),
      value: index + 1,
    })
  )
})

const hourOptions = Array.from(
  { length: 24 },
  (_, index) => padNumber(index)
)

const minuteOptions = Array.from(
  { length: 12 },
  (_, index) => padNumber(index * 5)
)

watch(
  [
    () => dateParts.day,
    () => dateParts.month,
    () => dateParts.year,
  ],
  ([day, month, year]) => {
    if (day && month && year) {
      form.date =
        `${year}-` +
        `${padNumber(month)}-` +
        `${padNumber(day)}`
    } else {
      form.date = ''
    }
  }
)

watch(
  [
    () => dateParts.month,
    () => dateParts.year,
  ],
  () => {
    if (!dateParts.day) {
      return
    }

    const selectedDayExists =
      dayOptions.value.some(
        (option) =>
          option.value === dateParts.day
      )

    if (!selectedDayExists) {
      dateParts.day = null
    }
  }
)


watch(
  [
    () => startTimeParts.hour,
    () => startTimeParts.minute,
  ],
  ([hour, minute]) => {
    form.startTime =
      hour !== null && minute !== null
        ? `${hour}:${minute}`
        : ''
  }
)

watch(
  [
    () => endTimeParts.hour,
    () => endTimeParts.minute,
  ],
  ([hour, minute]) => {
    form.endTime =
      hour !== null && minute !== null
        ? `${hour}:${minute}`
        : ''
  }
)

const formattedDate = computed(() => {
  if (!form.date) {
    return ''
  }

  const [year, month, day] =
    form.date.split('-')

  return `${day}.${month}.${year}.`
})

const spaceOptions = publicSpaces.map(
  (space) => ({
    title:
      `${space.name} — ` +
      `${space.price} € / ${space.unit}`,
    value: space.id,
  })
)

const selectedSpace = computed(() => {
  return (
    publicSpaces.find(
      (space) =>
        space.id === Number(form.spaceId)
    ) ?? null
  )
})

const selectedExtras = computed(() => {
  return extras.filter((extra) =>
    form.extras.includes(extra.title)
  )
})

function timeToMinutes(time) {
  if (!time) {
    return null
  }

  const [hours, minutes] = time
    .split(':')
    .map(Number)

  return hours * 60 + minutes
}

const durationHours = computed(() => {
  const start =
    timeToMinutes(form.startTime)

  const end =
    timeToMinutes(form.endTime)

  if (
    start === null ||
    end === null ||
    end <= start
  ) {
    return 0
  }

  return (end - start) / 60
})

const durationMinutes = computed(() => {
  const start =
    timeToMinutes(form.startTime)

  const end =
    timeToMinutes(form.endTime)

  if (
    start === null ||
    end === null ||
    end <= start
  ) {
    return 0
  }

  return end - start
})

function formatNumberWord(
  value,
  singular,
  few,
  many
) {
  const lastDigit = value % 10
  const lastTwoDigits = value % 100

  if (
    lastDigit === 1 &&
    lastTwoDigits !== 11
  ) {
    return `${value} ${singular}`
  }

  if (
    lastDigit >= 2 &&
    lastDigit <= 4 &&
    !(
      lastTwoDigits >= 12 &&
      lastTwoDigits <= 14
    )
  ) {
    return `${value} ${few}`
  }

  return `${value} ${many}`
}

const formattedDuration = computed(() => {
  const totalMinutes =
    durationMinutes.value

  if (!totalMinutes) {
    return ''
  }

  const hours =
    Math.floor(totalMinutes / 60)

  const minutes =
    totalMinutes % 60

  const parts = []

  if (hours > 0) {
    parts.push(
      formatNumberWord(
        hours,
        'sat',
        'sata',
        'sati'
      )
    )
  }

  if (minutes > 0) {
    parts.push(
      formatNumberWord(
        minutes,
        'minuta',
        'minute',
        'minuta'
      )
    )
  }

  return parts.join(' i ')
})

const basePrice = computed(() => {
  if (!selectedSpace.value) {
    return 0
  }

  if (
    selectedSpace.value.unit === 'sat' &&
    durationHours.value > 0
  ) {
    return (
      selectedSpace.value.price *
      durationHours.value
    )
  }

  return selectedSpace.value.price
})

const extrasPrice = computed(() => {
  return selectedExtras.value.reduce(
    (sum, extra) =>
      sum + extra.price,
    0
  )
})

const total = computed(() => {
  return Number(
    (
      basePrice.value +
      extrasPrice.value
    ).toFixed(2)
  )
})

function formatCurrency(value) {
  return new Intl.NumberFormat('hr-HR', {
    style: 'currency',
    currency: 'EUR',
  }).format(Number(value) || 0)
}

function validationForStep(targetStep) {
  if (targetStep === 1) {
    if (!selectedSpace.value) {
      return 'Odaberite prostor koji želite rezervirati.'
    }
  }

  if (targetStep === 2) {
    if (!form.date) {
      return 'Odaberite potpuni datum rezervacije.'
    }

    if (form.date < minimumDate) {
      return 'Datum rezervacije ne može biti u prošlosti.'
    }

    if (
      !form.startTime ||
      !form.endTime
    ) {
      return 'Odaberite vrijeme početka i završetka.'
    }

    const start =
      timeToMinutes(form.startTime)

    const end =
      timeToMinutes(form.endTime)

    if (
      start === null ||
      end === null ||
      end <= start
    ) {
      return 'Vrijeme završetka mora biti nakon vremena početka.'
    }

    if (
      !Number(form.guests) ||
      Number(form.guests) < 1
    ) {
      return 'Broj osoba mora biti najmanje 1.'
    }

    if (
      selectedSpace.value &&
      Number(form.guests) >
        selectedSpace.value.capacity
    ) {
      return (
        `Odabrani prostor prima najviše ` +
        `${selectedSpace.value.capacity} osoba.`
      )
    }
  }

  if (targetStep === 3) {
    if (!form.firstName.trim()) {
      return 'Unesite svoje ime.'
    }

    if (!form.lastName.trim()) {
      return 'Unesite svoje prezime.'
    }

    if (!form.email.trim()) {
      return 'Unesite e-mail adresu.'
    }

    const emailPattern =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    if (
      !emailPattern.test(
        form.email.trim()
      )
    ) {
      return 'Unesite ispravnu e-mail adresu.'
    }
  }

  return ''
}

function scrollToWizard() {
  requestAnimationFrame(() => {
    document
      .querySelector(
        '.public-wizard-wrap'
      )
      ?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
  })
}

function goNext() {
  const message =
    validationForStep(step.value)

  if (message) {
    validationMessage.value = message
    return
  }

  validationMessage.value = ''
  submitError.value = ''

  if (step.value < 5) {
    step.value += 1
    scrollToWizard()
  }
}

function goBack() {
  validationMessage.value = ''
  submitError.value = ''

  if (step.value > 1) {
    step.value -= 1
    scrollToWizard()
  }
}

function goToPreviousStep(targetStep) {
  if (targetStep < step.value) {
    step.value = targetStep
    validationMessage.value = ''
    submitError.value = ''
    scrollToWizard()
  }
}

async function submit() {
  submitError.value = ''
  validationMessage.value = ''

  for (
    const targetStep of [1, 2, 3]
  ) {
    const message =
      validationForStep(targetStep)

    if (message) {
      step.value = targetStep
      validationMessage.value = message
      scrollToWizard()
      return
    }
  }

  loading.value = true

  try {
    const result =
      await createPublicReservation({
        ...form,
        spaceName:
          selectedSpace.value.name,
        durationHours:
          durationHours.value,
        basePrice:
          basePrice.value,
        extrasPrice:
          extrasPrice.value,
        total:
          total.value,
      })

    sessionStorage.setItem(
      'publicReservation',
      JSON.stringify(result)
    )

    await router.push(
      '/rezervacija/potvrda'
    )
  } catch (error) {
    console.error(
      'Greška pri slanju rezervacije:',
      error
    )

    submitError.value =
      'Rezervaciju trenutno nije moguće poslati. Pokušajte ponovno.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="public-section">
    <div
      class="public-container public-wizard-wrap"
    >
      <div class="public-page-heading">
        <span class="public-eyebrow">
          REZERVACIJA
        </span>

        <h1>Rezervirajte prostor</h1>

        <p>
          Ispunite podatke kroz pet
          jednostavnih koraka. Obavezna
          polja označena su zvjezdicom.
        </p>
      </div>

      <div class="public-stepper-wrap">
        <div
          class="public-stepper"
          aria-label="Koraci rezervacije"
        >
          <button
            v-for="(label, index) in stepLabels"
            :key="label"
            type="button"
            :class="[
              'public-stepper__item',
              {
                'is-active':
                  index + 1 === step,
                'is-complete':
                  index + 1 < step,
              },
            ]"
            :disabled="index + 1 >= step"
            @click="
              goToPreviousStep(index + 1)
            "
          >
            <span>
              <v-icon
                v-if="index + 1 < step"
                icon="mdi-check"
                size="18"
              />

              <template v-else>
                {{ index + 1 }}
              </template>
            </span>

            <small>{{ label }}</small>
          </button>
        </div>
      </div>

      <v-card
        class="public-wizard-card"
        elevation="0"
      >
        <v-card-text
          class="public-wizard-card__content"
        >
          <v-alert
            v-if="validationMessage"
            type="warning"
            variant="tonal"
            closable
            class="public-wizard-alert"
            @click:close="
              validationMessage = ''
            "
          >
            {{ validationMessage }}
          </v-alert>

          <v-alert
            v-if="submitError"
            type="error"
            variant="tonal"
            closable
            class="public-wizard-alert"
            @click:close="
              submitError = ''
            "
          >
            {{ submitError }}
          </v-alert>


          <div
            v-if="step === 1"
            class="public-wizard-step"
          >
            <div
              class="public-wizard-step__heading"
            >
              <span>Korak 1 od 5</span>

              <h2>Odaberite prostor</h2>

              <p>
                Odaberite prostor koji najbolje
                odgovara vašem događaju ili
                načinu rada.
              </p>
            </div>

            <v-select
              v-model="form.spaceId"
              :items="spaceOptions"
              item-title="title"
              item-value="value"
              label="Prostor *"
              prepend-inner-icon="mdi-office-building-outline"
              variant="outlined"
              hide-details="auto"
            />

            <div
              v-if="selectedSpace"
              class="public-selected-space"
            >
              <div>
                <span
                  class="public-selected-space__label"
                >
                  Odabrani prostor
                </span>

                <h3>
                  {{ selectedSpace.name }}
                </h3>

                <p>
                  {{
                    selectedSpace.shortDescription
                  }}
                </p>
              </div>

              <div
                class="public-selected-space__facts"
              >
                <span>
                  <v-icon
                    icon="mdi-account-group-outline"
                    size="20"
                  />

                  Do
                  {{ selectedSpace.capacity }}
                  osoba
                </span>

                <strong>
                  {{
                    formatCurrency(
                      selectedSpace.price
                    )
                  }}
                  /
                  {{ selectedSpace.unit }}
                </strong>
              </div>
            </div>
          </div>


          <div
            v-else-if="step === 2"
            class="public-wizard-step"
          >
            <div
              class="public-wizard-step__heading"
            >
              <span>Korak 2 od 5</span>

              <h2>Odaberite termin</h2>

              <p>
                Prvo odaberite datum u formatu
                DD / MM / YYYY, a zatim početak
                i završetak u 24-satnom formatu.
              </p>
            </div>

            <div class="public-form-grid">
              <div
                class="public-date-field public-form-grid__wide"
              >
                <label
                  class="public-custom-field-label"
                >
                  Datum rezervacije *
                </label>

                <div class="public-date-grid">
                  <v-select
                    v-model="dateParts.day"
                    :items="dayOptions"
                    item-title="title"
                    item-value="value"
                    label="DD"
                    placeholder="DD"
                    variant="outlined"
                    hide-details="auto"
                  />

                  <v-select
                    v-model="dateParts.month"
                    :items="monthOptions"
                    item-title="title"
                    item-value="value"
                    label="MM"
                    placeholder="MM"
                    variant="outlined"
                    hide-details="auto"
                  />

                  <v-select
                    v-model="dateParts.year"
                    :items="yearOptions"
                    label="YYYY"
                    placeholder="YYYY"
                    variant="outlined"
                    hide-details="auto"
                  />
                </div>
              </div>

              <div class="public-time-block">
                <label
                  class="public-custom-field-label"
                >
                  Vrijeme početka *
                </label>

                <div class="public-time-grid">
                  <v-select
                    v-model="
                      startTimeParts.hour
                    "
                    :items="hourOptions"
                    label="Sat"
                    placeholder="13"
                    prepend-inner-icon="mdi-clock-start"
                    variant="outlined"
                    hide-details="auto"
                  />

                  <v-select
                    v-model="
                      startTimeParts.minute
                    "
                    :items="minuteOptions"
                    label="Minute"
                    placeholder="00"
                    variant="outlined"
                    hide-details="auto"
                  />
                </div>

                <p
                  v-if="form.startTime"
                  class="public-time-preview"
                >
                  Početak:
                  <strong>
                    {{ form.startTime }}
                  </strong>
                </p>
              </div>

              <div class="public-time-block">
                <label
                  class="public-custom-field-label"
                >
                  Vrijeme završetka *
                </label>

                <div class="public-time-grid">
                  <v-select
                    v-model="
                      endTimeParts.hour
                    "
                    :items="hourOptions"
                    label="Sat"
                    placeholder="15"
                    prepend-inner-icon="mdi-clock-end"
                    variant="outlined"
                    hide-details="auto"
                  />

                  <v-select
                    v-model="
                      endTimeParts.minute
                    "
                    :items="minuteOptions"
                    label="Minute"
                    placeholder="00"
                    variant="outlined"
                    hide-details="auto"
                  />
                </div>

                <p
                  v-if="form.endTime"
                  class="public-time-preview"
                >
                  Završetak:
                  <strong>
                    {{ form.endTime }}
                  </strong>
                </p>
              </div>

              <v-text-field
                v-model.number="form.guests"
                type="number"
                min="1"
                :max="
                  selectedSpace?.capacity
                "
                label="Broj osoba *"
                prepend-inner-icon="mdi-account-group-outline"
                variant="outlined"
                hide-details="auto"
                class="public-form-grid__wide"
              />
            </div>

            <v-alert
              v-if="durationHours > 0"
              type="info"
              variant="tonal"
              density="comfortable"
              class="public-duration-alert"
            >
              Odabrani termin:

              <strong>
                {{ formattedDate }},
                {{ form.startTime }}
                –
                {{ form.endTime }}
              </strong>

              <br>

              Trajanje:

              <strong>
                {{ formattedDuration }}
              </strong>
            </v-alert>
          </div>

          <div
            v-else-if="step === 3"
            class="public-wizard-step"
          >
            <div
              class="public-wizard-step__heading"
            >
              <span>Korak 3 od 5</span>

              <h2>
                Unesite svoje podatke
              </h2>

              <p>
                Podaci će se koristiti za
                potvrdu i kontakt vezan uz
                rezervaciju.
              </p>
            </div>

            <div class="public-form-grid">
              <v-text-field
                v-model="form.firstName"
                label="Ime *"
                autocomplete="given-name"
                prepend-inner-icon="mdi-account-outline"
                variant="outlined"
                hide-details="auto"
              />

              <v-text-field
                v-model="form.lastName"
                label="Prezime *"
                autocomplete="family-name"
                prepend-inner-icon="mdi-account-outline"
                variant="outlined"
                hide-details="auto"
              />

              <v-text-field
                v-model="form.email"
                type="email"
                label="E-mail *"
                autocomplete="email"
                prepend-inner-icon="mdi-email-outline"
                variant="outlined"
                hide-details="auto"
              />

              <v-text-field
                v-model="form.phone"
                type="tel"
                label="Telefon"
                autocomplete="tel"
                prepend-inner-icon="mdi-phone-outline"
                variant="outlined"
                hide-details="auto"
              />

              <v-text-field
                v-model="form.company"
                label="Tvrtka / organizacija"
                prepend-inner-icon="mdi-domain"
                variant="outlined"
                hide-details="auto"
                class="public-form-grid__wide"
              />

              <v-text-field
                v-model="form.eventName"
                label="Naziv događaja"
                prepend-inner-icon="mdi-calendar-star"
                variant="outlined"
                hide-details="auto"
                class="public-form-grid__wide"
              />

              <v-textarea
                v-model="form.note"
                label="Dodatna napomena"
                prepend-inner-icon="mdi-text-box-outline"
                variant="outlined"
                rows="3"
                auto-grow
                hide-details="auto"
                class="public-form-grid__wide"
              />
            </div>
          </div>


          <div
            v-else-if="step === 4"
            class="public-wizard-step"
          >
            <div
              class="public-wizard-step__heading"
            >
              <span>Korak 4 od 5</span>

              <h2>Dodatne usluge</h2>

              <p>
                Ovaj korak nije obavezan.
                Odaberite samo usluge koje
                su vam potrebne.
              </p>
            </div>

            <div class="public-extra-grid">
              <div
                v-for="extra in extras"
                :key="extra.title"
                class="public-extra-option"
              >
                <v-checkbox
                  v-model="form.extras"
                  :value="extra.title"
                  color="primary"
                  hide-details
                >
                  <template #label>
                    <div
                      class="public-extra-option__content"
                    >
                      <div>
                        <strong>
                          {{ extra.title }}
                        </strong>

                        <p>
                          {{
                            extra.description
                          }}
                        </p>
                      </div>

                      <span>
                        +{{
                          formatCurrency(
                            extra.price
                          )
                        }}
                      </span>
                    </div>
                  </template>
                </v-checkbox>
              </div>
            </div>
          </div>


          <div
            v-else
            class="public-wizard-step"
          >
            <div
              class="public-wizard-step__heading"
            >
              <span>Korak 5 od 5</span>

              <h2>
                Pregled rezervacije
              </h2>

              <p>
                Provjerite unesene podatke
                prije konačne potvrde
                rezervacije.
              </p>
            </div>

            <div class="public-summary">
              <div
                class="public-summary__section"
              >
                <h3>Prostor i termin</h3>

                <div
                  class="public-summary__row"
                >
                  <span>Prostor</span>

                  <strong>
                    {{ selectedSpace?.name }}
                  </strong>
                </div>

                <div
                  class="public-summary__row"
                >
                  <span>Datum</span>

                  <strong>
                    {{ formattedDate }}
                  </strong>
                </div>

                <div
                  class="public-summary__row"
                >
                  <span>Vrijeme</span>

                  <strong>
                    {{ form.startTime }}
                    –
                    {{ form.endTime }}
                  </strong>
                </div>

                <div
                  class="public-summary__row"
                >
                  <span>Broj osoba</span>

                  <strong>
                    {{ form.guests }}
                  </strong>
                </div>
              </div>

              <div
                class="public-summary__section"
              >
                <h3>Kontaktni podaci</h3>

                <div
                  class="public-summary__row"
                >
                  <span>Ime i prezime</span>

                  <strong>
                    {{ form.firstName }}
                    {{ form.lastName }}
                  </strong>
                </div>

                <div
                  class="public-summary__row"
                >
                  <span>E-mail</span>

                  <strong>
                    {{ form.email }}
                  </strong>
                </div>

                <div
                  v-if="form.phone"
                  class="public-summary__row"
                >
                  <span>Telefon</span>

                  <strong>
                    {{ form.phone }}
                  </strong>
                </div>

                <div
                  v-if="form.company"
                  class="public-summary__row"
                >
                  <span>Organizacija</span>

                  <strong>
                    {{ form.company }}
                  </strong>
                </div>

                <div
                  v-if="form.eventName"
                  class="public-summary__row"
                >
                  <span>
                    Naziv događaja
                  </span>

                  <strong>
                    {{ form.eventName }}
                  </strong>
                </div>

                <div
                  v-if="form.note"
                  class="public-summary__row"
                >
                  <span>Napomena</span>

                  <strong>
                    {{ form.note }}
                  </strong>
                </div>
              </div>

              <div
                class="public-summary__section"
              >
                <h3>Dodatne usluge</h3>

                <div
                  v-if="
                    selectedExtras.length
                  "
                  class="public-summary__extras"
                >
                  <div
                    v-for="
                      extra in selectedExtras
                    "
                    :key="extra.title"
                    class="public-summary__row"
                  >
                    <span>
                      {{ extra.title }}
                    </span>

                    <strong>
                      {{
                        formatCurrency(
                          extra.price
                        )
                      }}
                    </strong>
                  </div>
                </div>

                <p
                  v-else
                  class="public-summary__empty"
                >
                  Nisu odabrane dodatne
                  usluge.
                </p>
              </div>

              <div
                class="public-summary__price"
              >
                <div
                  class="public-summary__row"
                >
                  <span>
                    Najam prostora
                  </span>

                  <strong>
                    {{
                      formatCurrency(
                        basePrice
                      )
                    }}
                  </strong>
                </div>

                <div
                  class="public-summary__row"
                >
                  <span>
                    Dodatne usluge
                  </span>

                  <strong>
                    {{
                      formatCurrency(
                        extrasPrice
                      )
                    }}
                  </strong>
                </div>

                <div
                  class="public-summary__total"
                >
                  <span>Ukupno</span>

                  <strong>
                    {{
                      formatCurrency(total)
                    }}
                  </strong>
                </div>
              </div>

              <v-alert
                type="info"
                variant="tonal"
                class="public-payment-notice"
              >
                Plaćanje je trenutno
                demonstracijski korak dok se
                ne poveže Monri API.
              </v-alert>
            </div>
          </div>
        </v-card-text>

        <v-card-actions
          class="public-wizard-actions"
        >
          <v-btn
            v-if="step > 1"
            variant="outlined"
            prepend-icon="mdi-arrow-left"
            size="large"
            @click="goBack"
          >
            Nazad
          </v-btn>

          <span
            v-else
            class="public-wizard-actions__spacer"
          />

          <v-btn
            v-if="step < 5"
            color="primary"
            variant="flat"
            append-icon="mdi-arrow-right"
            size="large"
            @click="goNext"
          >
            Dalje
          </v-btn>

          <v-btn
            v-else
            color="primary"
            variant="flat"
            prepend-icon="mdi-check"
            size="large"
            :loading="loading"
            :disabled="loading"
            @click="submit"
          >
            Potvrdi rezervaciju
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </section>
</template>

<style scoped>
.public-custom-field-label {
  display: block;
  margin-bottom: 10px;
  color: #344054;
  font-size: 0.92rem;
  font-weight: 700;
}

.public-date-field,
.public-time-block {
  min-width: 0;
}

.public-date-grid {
  display: grid;
  grid-template-columns:
    minmax(90px, 0.7fr)
    minmax(90px, 0.7fr)
    minmax(130px, 1fr);
  gap: 14px;
}

.public-time-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.public-time-preview {
  margin: 8px 0 0;
  color: #667085;
  font-size: 0.88rem;
}

.public-time-preview strong {
  color: #24364b;
}

@media (max-width: 640px) {
  .public-date-grid {
    grid-template-columns:
      repeat(3, minmax(0, 1fr));
    gap: 8px;
  }

  .public-time-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 420px) {
  .public-date-grid {
    grid-template-columns: 1fr;
  }
}
</style>