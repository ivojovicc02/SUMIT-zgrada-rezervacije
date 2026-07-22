<script setup>
import {
  computed,
  onMounted,
  ref,
  watch,
} from 'vue'

import reservationService from '../../services/admin/reservationService'
import {
  getSpaces,
} from '../../services/admin/spaceService'

const search = ref('')
const selectedStatus = ref('all')
const selectedSpace = ref('all')
const dateFrom = ref('')
const dateTo = ref('')

const reservations = ref([])
const spaces = ref([])
const loading = ref(false)
const errorMessage = ref('')

const currentView = ref('list')
const calendarSpace = ref(null)
const currentWeekStart = ref(getStartOfWeek(new Date()))
const calendarStartHour = 8
const calendarEndHour = 22
const hourHeight = 64

const detailsDialog = ref(false)
const cancelDialog = ref(false)
const selectedReservation = ref(null)
const cancellationReason = ref('')

let searchTimer = null

const statusOptions = [
  { title: 'Svi statusi', value: 'all' },
  { title: 'Na čekanju', value: 'pending' },
  { title: 'Potvrđene', value: 'confirmed' },
  { title: 'Otkazane', value: 'cancelled' },
]

// Filtriranje se obavlja na backendu preko query parametara.
const filteredReservations = computed(() => reservations.value)

const calendarSpaceOptions = computed(() =>
  spaces.value.map((space) => ({
    title: space.name,
    value: space.id,
  })),
)

const spaceOptions = computed(() => [
  { title: 'Svi prostori', value: 'all' },
  ...spaces.value.map((space) => ({
    title: space.name,
    value: space.id,
  })),
])

const weekDays = computed(() => {
  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(currentWeekStart.value)
    date.setDate(date.getDate() + index)

    return {
      date,
      key: toDateKey(date),
      shortName: new Intl.DateTimeFormat('hr-HR', {
        weekday: 'short',
      }).format(date),
      dayNumber: date.getDate(),
      monthName: new Intl.DateTimeFormat('hr-HR', {
        month: 'short',
      }).format(date),
      isToday: toDateKey(date) === toDateKey(new Date()),
    }
  })
})

const calendarHours = computed(() =>
  Array.from(
    { length: calendarEndHour - calendarStartHour + 1 },
    (_, index) => calendarStartHour + index,
  ),
)

const calendarReservations = computed(() => {
  if (!calendarSpace.value) return []

  return reservations.value.filter((reservation) => {
    if (reservation.status === 'cancelled') return false

    const reservationSpaceId =
      reservation.space?.id ?? reservation.space_id

    if (
      Number(reservationSpaceId) !==
      Number(calendarSpace.value)
    ) {
      return false
    }

    const reservationDate = toDateKey(reservation.start_time)

    return weekDays.value.some(
      (day) => day.key === reservationDate,
    )
  })
})

const weekRangeLabel = computed(() => {
  const start = new Date(currentWeekStart.value)
  const end = new Date(currentWeekStart.value)
  end.setDate(end.getDate() + 6)

  const sameMonth =
    start.getMonth() === end.getMonth() &&
    start.getFullYear() === end.getFullYear()

  if (sameMonth) {
    return `${start.getDate()}. – ${end.getDate()}. ${new Intl.DateTimeFormat(
      'hr-HR',
      { month: 'long', year: 'numeric' },
    ).format(end)}`
  }

  return `${new Intl.DateTimeFormat('hr-HR', {
    day: 'numeric',
    month: 'short',
  }).format(start)} – ${new Intl.DateTimeFormat('hr-HR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(end)}`
})

const statistics = computed(() => {
  const total = reservations.value.length
  const confirmed = reservations.value.filter(
    (reservation) => reservation.status === 'confirmed',
  ).length
  const pending = reservations.value.filter(
    (reservation) => reservation.status === 'pending',
  ).length
  const cancelled = reservations.value.filter(
    (reservation) => reservation.status === 'cancelled',
  ).length

  return { total, confirmed, pending, cancelled }
})

async function loadSpaces() {
  try {
    const response = await getSpaces()

    spaces.value = Array.isArray(response.data)
      ? response.data
      : response.data?.items ?? []

    if (!calendarSpace.value && spaces.value.length > 0) {
      calendarSpace.value = spaces.value[0].id
    }
  } catch (error) {
    console.error('Greška pri dohvaćanju prostora:', error)

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće dohvatiti prostore.'
  }
}

function getSpaceName(reservation) {
  if (reservation.space?.name) {
    return reservation.space.name
  }

  const space = spaces.value.find(
    (item) =>
      Number(item.id) === Number(reservation.space_id),
  )

  return space?.name || 'Nepoznat prostor'
}

async function loadReservations() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await reservationService.getReservations({
      status: selectedStatus.value,
      spaceId: selectedSpace.value,
      search: search.value,
      fromDate: dateFrom.value,
      toDate: dateTo.value,
    })

    reservations.value = Array.isArray(response)
      ? response
      : response?.items ?? []
  } catch (error) {
    console.error('Greška pri dohvaćanju rezervacija:', error)
    reservations.value = []
    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće dohvatiti rezervacije.'
  } finally {
    loading.value = false
  }
}

function getStartOfWeek(dateValue) {
  const date = new Date(dateValue)
  const day = date.getDay()
  const difference = day === 0 ? -6 : 1 - day

  date.setDate(date.getDate() + difference)
  date.setHours(0, 0, 0, 0)
  return date
}

function toDateKey(dateValue) {
  const date = new Date(dateValue)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function changeWeek(offset) {
  const nextWeek = new Date(currentWeekStart.value)
  nextWeek.setDate(nextWeek.getDate() + offset * 7)
  currentWeekStart.value = nextWeek
}

function goToCurrentWeek() {
  currentWeekStart.value = getStartOfWeek(new Date())
}

function getReservationsForDay(dayKey) {
  return calendarReservations.value.filter(
    (reservation) =>
      toDateKey(reservation.start_time) === dayKey,
  )
}

function getCalendarEventStyle(reservation) {
  const start = new Date(reservation.start_time)
  const end = new Date(reservation.end_time)
  const startMinutes = start.getHours() * 60 + start.getMinutes()
  const endMinutes = end.getHours() * 60 + end.getMinutes()
  const calendarStartMinutes = calendarStartHour * 60
  const calendarEndMinutes = calendarEndHour * 60
  const visibleStart = Math.max(startMinutes, calendarStartMinutes)
  const visibleEnd = Math.min(endMinutes, calendarEndMinutes)
  const top = ((visibleStart - calendarStartMinutes) / 60) * hourHeight
  const height = Math.max(((visibleEnd - visibleStart) / 60) * hourHeight, 30)

  return { top: `${top}px`, height: `${height}px` }
}

function getCalendarEventClass(status) {
  return {
    'calendar-event--confirmed': status === 'confirmed',
    'calendar-event--pending': status === 'pending',
  }
}

function openDetails(reservation) {
  selectedReservation.value = reservation
  detailsDialog.value = true
}

function openCancelDialog(reservation) {
  selectedReservation.value = reservation
  cancellationReason.value = ''
  cancelDialog.value = true
}

function confirmReservation(reservation) {
  reservation.status = 'confirmed'
}

function cancelReservation() {
  if (!selectedReservation.value) return

  selectedReservation.value.status = 'cancelled'
  selectedReservation.value.cancellation_reason =
    cancellationReason.value.trim() ||
    'Rezervacija je otkazana od strane administratora.'

  cancelDialog.value = false
  cancellationReason.value = ''
}

function clearFilters() {
  search.value = ''
  selectedStatus.value = 'all'
  selectedSpace.value = 'all'
  dateFrom.value = ''
  dateTo.value = ''
}

function getStatusLabel(status) {
  const labels = {
    pending: 'Na čekanju',
    confirmed: 'Potvrđena',
    cancelled: 'Otkazana',
  }
  return labels[status] || status
}

function getStatusColor(status) {
  const colors = {
    pending: 'warning',
    confirmed: 'success',
    cancelled: 'error',
  }
  return colors[status] || 'grey'
}

function formatDate(dateValue) {
  if (!dateValue) return '—'

  return new Intl.DateTimeFormat('hr-HR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(dateValue))
}

function formatTime(dateValue) {
  if (!dateValue) return '—'

  return new Intl.DateTimeFormat('hr-HR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(dateValue))
}

function formatDateTime(dateValue) {
  if (!dateValue) return '—'

  return new Intl.DateTimeFormat('hr-HR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(dateValue))
}

function formatCurrency(value) {
  return new Intl.NumberFormat('hr-HR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value) || 0)
}

watch(
  [selectedStatus, selectedSpace, dateFrom, dateTo],
  loadReservations,
)

watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadReservations, 400)
})

onMounted(async () => {
  await Promise.all([
    loadSpaces(),
    loadReservations(),
  ])
})
</script>

<template>
  <section class="reservations-page">
    <header class="page-header">
      <div>

        <h1>Rezervacije</h1>

        <p class="page-description">
          Pregledajte, filtrirajte i upravljajte
          rezervacijama prostora.
        </p>
      </div>

      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
      >
        Nova rezervacija
      </v-btn>
    </header>

    <div class="statistics-grid">
      <v-card class="stat-card" elevation="0">
        <div class="stat-card__icon stat-card__icon--blue">
          <v-icon icon="mdi-calendar-month" />
        </div>

        <div>
          <span>Ukupno rezervacija</span>
          <strong>{{ statistics.total }}</strong>
        </div>
      </v-card>

      <v-card class="stat-card" elevation="0">
        <div class="stat-card__icon stat-card__icon--green">
          <v-icon icon="mdi-check-circle-outline" />
        </div>

        <div>
          <span>Potvrđene</span>
          <strong>{{ statistics.confirmed }}</strong>
        </div>
      </v-card>

      <v-card class="stat-card" elevation="0">
        <div class="stat-card__icon stat-card__icon--orange">
          <v-icon icon="mdi-clock-outline" />
        </div>

        <div>
          <span>Na čekanju</span>
          <strong>{{ statistics.pending }}</strong>
        </div>
      </v-card>

      <v-card class="stat-card" elevation="0">
        <div class="stat-card__icon stat-card__icon--red">
          <v-icon icon="mdi-close-circle-outline" />
        </div>

        <div>
          <span>Otkazane</span>
          <strong>{{ statistics.cancelled }}</strong>
        </div>
      </v-card>
    </div>

    <v-card class="filters-card" elevation="0">
      <div class="filters-grid">
        <v-text-field
          v-model="search"
          label="Pretraži rezervacije"
          placeholder="Događaj, korisnik, e-mail ili prostor"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="comfortable"
          hide-details
          clearable
        />

        <v-select
          v-model="selectedStatus"
          :items="statusOptions"
          label="Status"
          variant="outlined"
          density="comfortable"
          hide-details
        />

        <v-select
          v-model="selectedSpace"
          :items="spaceOptions"
          label="Prostor"
          variant="outlined"
          density="comfortable"
          hide-details
        />

        <v-text-field
          v-model="dateFrom"
          label="Datum od"
          type="date"
          variant="outlined"
          density="comfortable"
          hide-details
        />

        <v-text-field
          v-model="dateTo"
          label="Datum do"
          type="date"
          variant="outlined"
          density="comfortable"
          hide-details
        />

        <v-btn
          variant="tonal"
          prepend-icon="mdi-filter-remove-outline"
          height="48"
          @click="clearFilters"
        >
          Očisti
        </v-btn>
      </div>
    </v-card>

    <v-alert
      v-if="errorMessage"
      type="error"
      variant="tonal"
      closable
      class="mb-4"
      @click:close="errorMessage = ''"
    >
      {{ errorMessage }}
    </v-alert>

    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      class="mb-3"
    />

    <v-card class="reservations-card" elevation="0">
      <div class="table-header">
        <div>
          <h2>{{ currentView === 'list' ? 'Popis rezervacija' : 'Tjedni kalendar' }}</h2>

          <p v-if="currentView === 'list'">
            Prikazano {{ filteredReservations.length }} od {{ reservations.length }} rezervacija
          </p>
          <p v-else>{{ weekRangeLabel }}</p>
        </div>

        <div class="view-actions">
          <v-tooltip text="Prikaz liste">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-format-list-bulleted"
                :variant="currentView === 'list' ? 'tonal' : 'text'"
                :color="currentView === 'list' ? 'primary' : undefined"
                size="small"
                @click="currentView = 'list'"
              />
            </template>
          </v-tooltip>

          <v-tooltip text="Kalendarski prikaz">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-calendar-week"
                :variant="currentView === 'calendar' ? 'tonal' : 'text'"
                :color="currentView === 'calendar' ? 'primary' : undefined"
                size="small"
                @click="currentView = 'calendar'"
              />
            </template>
          </v-tooltip>
        </div>
      </div>

      <div
        v-if="currentView === 'list' && filteredReservations.length"
        class="table-wrapper"
      >
        <table class="reservations-table">
          <thead>
            <tr>
              <th>Događaj</th>
              <th>Korisnik</th>
              <th>Prostor</th>
              <th>Termin</th>
              <th>Gosti</th>
              <th>Iznos</th>
              <th>Status</th>
              <th class="actions-column">
                Akcije
              </th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="reservation in filteredReservations"
              :key="reservation.id"
            >
              <td>
                <div class="event-cell">
                  <strong>
                    {{ reservation.event_name }}
                  </strong>

                  <span>
                    #{{ reservation.id }}
                  </span>

                  <v-chip
                    v-if="reservation.recurring_rule"
                    size="x-small"
                    color="primary"
                    variant="tonal"
                    prepend-icon="mdi-repeat"
                  >
                    Ponavljajuća
                  </v-chip>
                </div>
              </td>

              <td>
                <div class="user-cell">
                  <strong>
                    {{ reservation.first_name }}
                    {{ reservation.last_name }}
                  </strong>

                  <span>
                    {{ reservation.email }}
                  </span>
                </div>
              </td>

              <td>
                <div class="space-cell">
                  <v-icon
                    icon="mdi-office-building-outline"
                    size="18"
                  />

                  <span>
                    {{ getSpaceName(reservation) }}
                  </span>
                </div>
              </td>

              <td>
                <div class="date-cell">
                  <strong>
                    {{
                      formatDate(
                        reservation.start_time,
                      )
                    }}
                  </strong>

                  <span>
                    {{
                      formatTime(
                        reservation.start_time,
                      )
                    }}
                    –
                    {{
                      formatTime(
                        reservation.end_time,
                      )
                    }}
                  </span>
                </div>
              </td>

              <td>
                <div class="guest-cell">
                  <v-icon
                    icon="mdi-account-group-outline"
                    size="18"
                  />

                  {{ reservation.guest_count }}
                </div>
              </td>

              <td>
                <strong>
                  {{
                    formatCurrency(
                      reservation.total_price,
                    )
                  }}
                  KM
                </strong>
              </td>

              <td>
                <v-chip
                  :color="
                    getStatusColor(
                      reservation.status,
                    )
                  "
                  size="small"
                  variant="tonal"
                >
                  {{
                    getStatusLabel(
                      reservation.status,
                    )
                  }}
                </v-chip>
              </td>

              <td>
                <div class="row-actions">
                  <v-tooltip text="Detalji">
                    <template #activator="{ props }">
                      <v-btn
                        v-bind="props"
                        icon="mdi-eye-outline"
                        variant="text"
                        size="small"
                        @click="openDetails(reservation)"
                      />
                    </template>
                  </v-tooltip>

                  <v-tooltip
                    v-if="
                      reservation.status === 'pending'
                    "
                    text="Potvrdi rezervaciju"
                  >
                    <template #activator="{ props }">
                      <v-btn
                        v-bind="props"
                        icon="mdi-check"
                        color="success"
                        variant="text"
                        size="small"
                        @click="
                          confirmReservation(reservation)
                        "
                      />
                    </template>
                  </v-tooltip>

                  <v-tooltip
                    v-if="
                      reservation.status !==
                      'cancelled'
                    "
                    text="Otkaži rezervaciju"
                  >
                    <template #activator="{ props }">
                      <v-btn
                        v-bind="props"
                        icon="mdi-close"
                        color="error"
                        variant="text"
                        size="small"
                        @click="
                          openCancelDialog(
                            reservation,
                          )
                        "
                      />
                    </template>
                  </v-tooltip>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="currentView === 'calendar'" class="calendar-view">
        <div class="calendar-toolbar">
          <div class="calendar-navigation">
            <v-btn icon="mdi-chevron-left" variant="text" size="small" @click="changeWeek(-1)" />
            <v-btn variant="tonal" size="small" @click="goToCurrentWeek">Danas</v-btn>
            <v-btn icon="mdi-chevron-right" variant="text" size="small" @click="changeWeek(1)" />
            <strong>{{ weekRangeLabel }}</strong>
          </div>

          <v-select
            v-model="calendarSpace"
            :items="calendarSpaceOptions"
            label="Prostor"
            variant="outlined"
            density="compact"
            hide-details
            class="calendar-space-select"
          />
        </div>

        <div class="calendar-scroll">
          <div class="calendar-grid">
            <div class="calendar-corner" />

            <div
              v-for="day in weekDays"
              :key="day.key"
              class="calendar-day-header"
              :class="{ 'calendar-day-header--today': day.isToday }"
            >
              <span>{{ day.shortName }}</span>
              <strong>{{ day.dayNumber }}</strong>
              <small>{{ day.monthName }}</small>
            </div>

            <div class="calendar-time-column">
              <div
                v-for="hour in calendarHours"
                :key="hour"
                class="calendar-time-label"
                :style="{ height: `${hourHeight}px` }"
              >
                {{ String(hour).padStart(2, '0') }}:00
              </div>
            </div>

            <div
              v-for="day in weekDays"
              :key="`column-${day.key}`"
              class="calendar-day-column"
              :class="{ 'calendar-day-column--today': day.isToday }"
              :style="{ height: `${(calendarEndHour - calendarStartHour + 1) * hourHeight}px` }"
            >
              <div
                v-for="hour in calendarHours"
                :key="`${day.key}-${hour}`"
                class="calendar-hour-line"
                :style="{
                  top: `${(hour - calendarStartHour) * hourHeight}px`,
                  height: `${hourHeight}px`,
                }"
              />

              <button
                v-for="reservation in getReservationsForDay(day.key)"
                :key="reservation.id"
                type="button"
                class="calendar-event"
                :class="getCalendarEventClass(reservation.status)"
                :style="getCalendarEventStyle(reservation)"
                @click="openDetails(reservation)"
              >
                <strong>{{ reservation.event_name }}</strong>
                <span>{{ formatTime(reservation.start_time) }} – {{ formatTime(reservation.end_time) }}</span>
                <small>{{ reservation.first_name }} {{ reservation.last_name }}</small>
              </button>
            </div>
          </div>
        </div>

        <div v-if="!calendarReservations.length" class="calendar-empty-state">
          <v-icon icon="mdi-calendar-blank-outline" size="44" color="grey-lighten-1" />
          <div>
            <strong>Nema rezervacija u ovom tjednu</strong>
            <p>Za odabrani prostor nema aktivnih rezervacija u prikazanom razdoblju.</p>
          </div>
        </div>
      </div>

      <div
        v-else-if="currentView === 'list' && !filteredReservations.length"
        class="empty-state"
      >
        <v-icon
          icon="mdi-calendar-remove-outline"
          size="64"
          color="grey-lighten-1"
        />

        <h3>Nema pronađenih rezervacija</h3>

        <p>
          Pokušajte promijeniti ili ukloniti
          postavljene filtre.
        </p>

        <v-btn
          variant="tonal"
          prepend-icon="mdi-filter-remove-outline"
          @click="clearFilters"
        >
          Očisti filtre
        </v-btn>
      </div>
    </v-card>

    <v-dialog
      v-model="detailsDialog"
      max-width="850"
    >
      <v-card
        v-if="selectedReservation"
        class="details-dialog"
      >
        <v-card-title class="dialog-header">
          <div>
            <span class="dialog-eyebrow">
              Rezervacija #{{ selectedReservation.id }}
            </span>

            <h2>
              {{ selectedReservation.event_name }}
            </h2>
          </div>

          <v-btn
            icon="mdi-close"
            variant="text"
            @click="detailsDialog = false"
          />
        </v-card-title>

        <v-divider />

        <v-card-text>
          <div class="details-status-row">
            <v-chip
              :color="
                getStatusColor(
                  selectedReservation.status,
                )
              "
              variant="tonal"
            >
              {{
                getStatusLabel(
                  selectedReservation.status,
                )
              }}
            </v-chip>

            <span>
              Kreirano:
              {{
                formatDateTime(
                  selectedReservation.created_at,
                )
              }}
            </span>
          </div>

          <div class="details-grid">
            <section class="details-section">
              <h3>
                <v-icon
                  icon="mdi-calendar-clock-outline"
                />
                Podaci o rezervaciji
              </h3>

              <dl>
                <div>
                  <dt>Prostor</dt>
                  <dd>
                    {{
                      {{ getSpaceName(selectedReservation) }}
                    }}
                  </dd>
                </div>

                <div>
                  <dt>Početak</dt>
                  <dd>
                    {{
                      formatDateTime(
                        selectedReservation.start_time,
                      )
                    }}
                  </dd>
                </div>

                <div>
                  <dt>Završetak</dt>
                  <dd>
                    {{
                      formatDateTime(
                        selectedReservation.end_time,
                      )
                    }}
                  </dd>
                </div>

                <div>
                  <dt>Broj gostiju</dt>
                  <dd>
                    {{
                      selectedReservation.guest_count
                    }}
                  </dd>
                </div>

                <div>
                  <dt>Ukupan iznos</dt>
                  <dd class="price-value">
                    {{
                      formatCurrency(
                        selectedReservation.total_price,
                      )
                    }}
                    KM
                  </dd>
                </div>
              </dl>
            </section>

            <section class="details-section">
              <h3>
                <v-icon
                  icon="mdi-account-outline"
                />
                Podaci korisnika
              </h3>

              <dl>
                <div>
                  <dt>Ime i prezime</dt>
                  <dd>
                    {{
                      selectedReservation.first_name
                    }}
                    {{
                      selectedReservation.last_name
                    }}
                  </dd>
                </div>

                <div>
                  <dt>E-mail</dt>
                  <dd>
                    {{ selectedReservation.email }}
                  </dd>
                </div>

                <div>
                  <dt>Telefon</dt>
                  <dd>
                    {{ selectedReservation.phone }}
                  </dd>
                </div>

                <div>
                  <dt>Tvrtka</dt>
                  <dd>
                    {{
                      selectedReservation.company ||
                      'Nije navedena'
                    }}
                  </dd>
                </div>
              </dl>
            </section>
          </div>

          <section class="details-section full-width">
            <h3>
              <v-icon
                icon="mdi-room-service-outline"
              />
              Dodatne usluge
            </h3>

            <div
              v-if="
                (selectedReservation.services?.length || 0)
              "
              class="services-list"
            >
              <div
                v-for="item in (selectedReservation.services || [])"
                :key="item.id"
                class="service-row"
              >
                <span>
                  {{ item.service.name }}
                </span>

                <strong>
                  {{
                    formatCurrency(
                      item.price_at_booking,
                    )
                  }}
                  KM
                </strong>
              </div>
            </div>

            <p v-else class="muted-text">
              Za ovu rezervaciju nisu odabrane
              dodatne usluge.
            </p>
          </section>

          <section
            v-if="selectedReservation.recurring_rule"
            class="details-section full-width recurring-box"
          >
            <h3>
              <v-icon icon="mdi-repeat" />
              Ponavljajuća rezervacija
            </h3>

            <p>
              Rezervacija se ponavlja
              <strong>
                {{
                  selectedReservation.recurring_rule
                    .type === 'weekly'
                    ? 'tjedno'
                    : 'dnevno'
                }}
              </strong>

              svakih

              <strong>
                {{
                  selectedReservation.recurring_rule
                    .interval
                }}
              </strong>

              {{
                selectedReservation.recurring_rule
                  .type === 'weekly'
                  ? 'tjedan'
                  : 'dan'
              }}

              do

              <strong>
                {{
                  formatDate(
                    selectedReservation
                      .recurring_rule.end_date,
                  )
                }}
              </strong>.
            </p>
          </section>

          <section
            v-if="selectedReservation.notes"
            class="details-section full-width"
          >
            <h3>
              <v-icon icon="mdi-note-text-outline" />
              Napomena
            </h3>

            <p>
              {{ selectedReservation.notes }}
            </p>
          </section>

          <v-alert
            v-if="
              selectedReservation.status ===
                'cancelled' &&
              selectedReservation.cancellation_reason
            "
            type="error"
            variant="tonal"
            title="Rezervacija je otkazana"
          >
            {{
              selectedReservation
                .cancellation_reason
            }}
          </v-alert>
        </v-card-text>

        <v-divider />

        <v-card-actions class="dialog-actions">
          <v-btn
            variant="text"
            @click="detailsDialog = false"
          >
            Zatvori
          </v-btn>

          <v-spacer />

          <v-btn
            v-if="
              selectedReservation.status === 'pending'
            "
            color="success"
            variant="tonal"
            prepend-icon="mdi-check"
            @click="
              confirmReservation(
                selectedReservation,
              )
            "
          >
            Potvrdi
          </v-btn>

          <v-btn
            v-if="
              selectedReservation.status !==
              'cancelled'
            "
            color="error"
            prepend-icon="mdi-close"
            @click="
              detailsDialog = false;
              openCancelDialog(
                selectedReservation,
              )
            "
          >
            Otkaži rezervaciju
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog
      v-model="cancelDialog"
      max-width="520"
    >
      <v-card>
        <v-card-title class="cancel-dialog-title">
          <v-icon
            icon="mdi-alert-circle-outline"
            color="error"
          />

          Otkaži rezervaciju
        </v-card-title>

        <v-card-text>
          <p>
            Jeste li sigurni da želite otkazati
            rezervaciju
            <strong>
              {{ selectedReservation?.event_name }}
            </strong>?
          </p>

          <v-textarea
            v-model="cancellationReason"
            label="Razlog otkazivanja"
            placeholder="Unesite razlog otkazivanja rezervacije"
            variant="outlined"
            rows="3"
            class="mt-4"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer />

          <v-btn
            variant="text"
            @click="cancelDialog = false"
          >
            Odustani
          </v-btn>

          <v-btn
            color="error"
            @click="cancelReservation"
          >
            Otkaži rezervaciju
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </section>
</template>


<style scoped>
.reservations-page {
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

.eyebrow,
.dialog-eyebrow {
  margin: 0 0 6px;
  color: rgb(var(--v-theme-primary));
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.page-header h1 {
  margin: 0;
  color: #0f172a;
  font-size: clamp(28px, 3vw, 36px);
}

.page-description {
  margin: 7px 0 0;
  color: #64748b;
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
}

.stat-card__icon {
  display: grid;
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  place-items: center;
  border-radius: 12px;
}

.stat-card__icon--blue {
  background: #eff6ff;
  color: #2563eb;
}

.stat-card__icon--green {
  background: #ecfdf5;
  color: #059669;
}

.stat-card__icon--orange {
  background: #fff7ed;
  color: #ea580c;
}

.stat-card__icon--red {
  background: #fff1f2;
  color: #e11d48;
}

.stat-card span,
.stat-card strong {
  display: block;
}

.stat-card span {
  color: #64748b;
  font-size: 12px;
}

.stat-card strong {
  margin-top: 3px;
  color: #0f172a;
  font-size: 24px;
}

.filters-card,
.reservations-card {
  border: 1px solid #e2e8f0;
  border-radius: 15px;
}

.filters-card {
  padding: 18px;
}

.filters-grid {
  display: grid;
  grid-template-columns:
    minmax(240px, 1.5fr)
    minmax(150px, 0.8fr)
    minmax(190px, 1fr)
    minmax(145px, 0.7fr)
    minmax(145px, 0.7fr)
    auto;
  align-items: center;
  gap: 13px;
}

.reservations-card {
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px 22px;
  border-bottom: 1px solid #e2e8f0;
}

.table-header h2 {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
}

.table-header p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 12px;
}

.view-actions {
  display: flex;
  gap: 5px;
}

.table-wrapper {
  overflow-x: auto;
}

.reservations-table {
  width: 100%;
  border-collapse: collapse;
}

.reservations-table th {
  padding: 13px 15px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  font-size: 11px;
  font-weight: 700;
  text-align: left;
  text-transform: uppercase;
  white-space: nowrap;
}

.reservations-table td {
  min-width: 110px;
  padding: 15px;
  border-bottom: 1px solid #f1f5f9;
  color: #475569;
  font-size: 13px;
  vertical-align: middle;
}

.reservations-table tbody tr {
  transition: background 0.2s ease;
}

.reservations-table tbody tr:hover {
  background: #f8fafc;
}

.reservations-table tbody tr:last-child td {
  border-bottom: 0;
}

.event-cell,
.user-cell,
.date-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.event-cell {
  min-width: 210px;
}

.user-cell {
  min-width: 190px;
}

.event-cell strong,
.user-cell strong,
.date-cell strong {
  color: #0f172a;
}

.event-cell span,
.user-cell span,
.date-cell span {
  color: #94a3b8;
  font-size: 11px;
}

.space-cell,
.guest-cell {
  display: flex;
  align-items: center;
  gap: 7px;
}

.space-cell {
  min-width: 180px;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.actions-column {
  text-align: center !important;
}

.empty-state {
  display: flex;
  min-height: 330px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 35px;
  text-align: center;
}

.empty-state h3 {
  margin: 15px 0 5px;
  color: #0f172a;
}

.empty-state p {
  margin: 0 0 18px;
  color: #94a3b8;
}

.dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 22px 24px;
}

.dialog-header h2 {
  margin: 0;
  color: #0f172a;
  font-size: 21px;
}

.details-dialog :deep(.v-card-text) {
  padding: 22px 24px;
}

.details-status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
}

.details-status-row > span {
  color: #94a3b8;
  font-size: 12px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.details-section {
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.details-section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px;
  color: #0f172a;
  font-size: 15px;
}

.details-section dl {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
}

.details-section dl div {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.details-section dt {
  color: #94a3b8;
  font-size: 12px;
}

.details-section dd {
  margin: 0;
  color: #334155;
  font-size: 13px;
  font-weight: 600;
  text-align: right;
}

.full-width {
  margin-top: 18px;
}

.price-value {
  color: #059669 !important;
}

.services-list {
  display: flex;
  flex-direction: column;
}

.service-row {
  display: flex;
  justify-content: space-between;
  padding: 9px 0;
  border-bottom: 1px solid #f1f5f9;
}

.service-row:last-child {
  border-bottom: 0;
}

.recurring-box {
  border-color: #bfdbfe;
  background: #eff6ff;
}

.recurring-box p,
.details-section > p {
  margin: 0;
  color: #475569;
  font-size: 13px;
  line-height: 1.65;
}

.muted-text {
  color: #94a3b8 !important;
}

.dialog-actions {
  padding: 14px 20px;
}

.cancel-dialog-title {
  display: flex;
  align-items: center;
  gap: 9px;
}


.calendar-view { background: #fff; }
.calendar-toolbar { display:flex; align-items:center; justify-content:space-between; gap:18px; padding:16px 20px; border-bottom:1px solid #e2e8f0; }
.calendar-navigation { display:flex; align-items:center; gap:8px; }
.calendar-navigation strong { margin-left:8px; color:#0f172a; font-size:14px; text-transform:capitalize; }
.calendar-space-select { max-width:290px; }
.calendar-scroll { overflow:auto; max-height:760px; }
.calendar-grid { display:grid; grid-template-columns:76px repeat(7,minmax(145px,1fr)); min-width:1090px; background:#fff; }
.calendar-corner { position:sticky; top:0; left:0; z-index:5; min-height:76px; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; background:#f8fafc; }
.calendar-day-header { position:sticky; top:0; z-index:4; display:flex; min-height:76px; flex-direction:column; align-items:center; justify-content:center; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; background:#f8fafc; }
.calendar-day-header span { color:#64748b; font-size:11px; font-weight:700; text-transform:uppercase; }
.calendar-day-header strong { margin-top:2px; color:#0f172a; font-size:22px; line-height:1; }
.calendar-day-header small { margin-top:3px; color:#94a3b8; font-size:10px; text-transform:capitalize; }
.calendar-day-header--today strong { display:grid; width:34px; height:34px; place-items:center; border-radius:50%; background:rgb(var(--v-theme-primary)); color:#fff; }
.calendar-time-column { position:sticky; left:0; z-index:3; border-right:1px solid #e2e8f0; background:#fff; }
.calendar-time-label { padding:7px 10px 0 0; border-bottom:1px solid #f1f5f9; color:#94a3b8; font-size:11px; text-align:right; }
.calendar-day-column { position:relative; overflow:hidden; border-right:1px solid #e2e8f0; background:#fff; }
.calendar-day-column--today { background:#f8fbff; }
.calendar-hour-line { position:absolute; right:0; left:0; border-bottom:1px solid #f1f5f9; pointer-events:none; }
.calendar-event { position:absolute; right:5px; left:5px; z-index:2; display:flex; min-height:30px; flex-direction:column; align-items:flex-start; overflow:hidden; padding:6px 8px; border:0; border-left:4px solid; border-radius:7px; cursor:pointer; text-align:left; transition:transform .15s ease,box-shadow .15s ease; }
.calendar-event:hover { z-index:3; transform:translateY(-1px); box-shadow:0 6px 16px rgb(15 23 42 / 14%); }
.calendar-event strong { width:100%; overflow:hidden; font-size:11px; line-height:1.25; text-overflow:ellipsis; white-space:nowrap; }
.calendar-event span,.calendar-event small { margin-top:2px; font-size:10px; line-height:1.2; }
.calendar-event--confirmed { border-left-color:#2563eb; background:#dbeafe; color:#1e3a8a; }
.calendar-event--pending { border-left-color:#ea580c; background:#ffedd5; color:#9a3412; }
.calendar-empty-state { display:flex; align-items:center; justify-content:center; gap:14px; padding:24px; border-top:1px solid #e2e8f0; background:#f8fafc; }
.calendar-empty-state strong { color:#334155; font-size:14px; }
.calendar-empty-state p { margin:3px 0 0; color:#94a3b8; font-size:12px; }

@media (max-width: 1280px) {
  .statistics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filters-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 800px) {
  .calendar-toolbar { align-items:stretch; flex-direction:column; }
  .calendar-space-select { max-width:none; }
  .calendar-navigation { flex-wrap:wrap; }
  .calendar-navigation strong { width:100%; margin:4px 0 0; }

  .page-header {
    flex-direction: column;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .filters-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .statistics-grid,
  .filters-grid {
    grid-template-columns: 1fr;
  }

  .details-status-row {
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
  }
}
</style>