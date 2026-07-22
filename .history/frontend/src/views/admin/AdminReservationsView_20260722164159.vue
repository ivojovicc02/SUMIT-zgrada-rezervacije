<script setup>
import { computed, ref } from 'vue'


const search = ref('')
const selectedStatus = ref('all')
const selectedSpace = ref('all')
const dateFrom = ref('')
const dateTo = ref('')

const currentView = ref('list')
const calendarSpace = ref(1)
const currentWeekStart = ref(getStartOfWeek(new Date('2026-07-20T00:00:00')))
const calendarStartHour = 8
const calendarEndHour = 22
const hourHeight = 64

const detailsDialog = ref(false)
const cancelDialog = ref(false)

const selectedReservation = ref(null)
const cancellationReason = ref('')

const statusOptions = [
  {
    title: 'Svi statusi',
    value: 'all',
  },
  {
    title: 'Na čekanju',
    value: 'pending',
  },
  {
    title: 'Potvrđene',
    value: 'confirmed',
  },
  {
    title: 'Otkazane',
    value: 'cancelled',
  },
]

const spaces = [
  {
    id: 1,
    name: 'Konferencijska dvorana A',
  },
  {
    id: 2,
    name: 'Konferencijska dvorana B',
  },
  {
    id: 3,
    name: 'Multimedijalna dvorana',
  },
  {
    id: 4,
    name: 'Ured 204',
  },
  {
    id: 5,
    name: 'Vanjski prostor',
  },
]

const reservations = ref([
  {
    id: 1,
    event_name: 'Radionica umjetne inteligencije',
    guest_count: 80,

    first_name: 'Ivan',
    last_name: 'Marić',
    email: 'ivan.maric@example.com',
    phone: '+387 63 111 222',
    company: 'SUMIT',

    start_time: '2026-07-23T09:00:00',
    end_time: '2026-07-23T12:00:00',

    total_price: 450,
    status: 'confirmed',
    notes: 'Potreban pristup prostoru 30 minuta ranije.',

    google_event_id: 'google-event-1',

    space: {
      id: 1,
      name: 'Konferencijska dvorana A',
      capacity: 120,
    },

    services: [
      {
        id: 1,
        price_at_booking: 30,
        service: {
          id: 1,
          name: 'Projektor',
        },
      },
      {
        id: 2,
        price_at_booking: 100,
        service: {
          id: 2,
          name: 'Ozvučenje',
        },
      },
    ],

    recurring_rule: null,
    created_at: '2026-07-18T14:20:00',
  },

  {
    id: 2,
    event_name: 'Sastanak projektnog tima',
    guest_count: 12,

    first_name: 'Ana',
    last_name: 'Kovač',
    email: 'ana.kovac@example.com',
    phone: '+387 63 333 444',
    company: 'Algebra Solutions',

    start_time: '2026-07-23T13:00:00',
    end_time: '2026-07-23T15:00:00',

    total_price: 120,
    status: 'pending',
    notes: null,

    google_event_id: null,

    space: {
      id: 4,
      name: 'Ured 204',
      capacity: 15,
    },

    services: [],

    recurring_rule: {
      id: 1,
      type: 'weekly',
      interval: 1,
      end_date: '2026-09-30T00:00:00',
    },

    created_at: '2026-07-19T10:15:00',
  },

  {
    id: 3,
    event_name: 'Prezentacija diplomskih radova',
    guest_count: 160,

    first_name: 'Marko',
    last_name: 'Jurić',
    email: 'marko.juric@example.com',
    phone: '+387 63 555 666',
    company: 'Sveučilište u Mostaru',

    start_time: '2026-07-24T10:00:00',
    end_time: '2026-07-24T14:00:00',

    total_price: 720,
    status: 'confirmed',
    notes: 'Potrebno pripremiti dva mikrofona.',

    google_event_id: 'google-event-3',

    space: {
      id: 3,
      name: 'Multimedijalna dvorana',
      capacity: 200,
    },

    services: [
      {
        id: 3,
        price_at_booking: 80,
        service: {
          id: 2,
          name: 'Ozvučenje',
        },
      },
      {
        id: 4,
        price_at_booking: 150,
        service: {
          id: 3,
          name: 'Tehnička podrška',
        },
      },
    ],

    recurring_rule: null,
    created_at: '2026-07-20T08:45:00',
  },

  {
    id: 4,
    event_name: 'Poslovna konferencija',
    guest_count: 250,

    first_name: 'Petra',
    last_name: 'Babić',
    email: 'petra.babic@example.com',
    phone: '+387 63 777 888',
    company: 'Tech Mostar',

    start_time: '2026-07-25T08:00:00',
    end_time: '2026-07-25T17:00:00',

    total_price: 1450,
    status: 'cancelled',
    notes: 'Cjelodnevni događaj.',

    cancellation_reason:
      'Organizator je odgodio konferenciju.',

    google_event_id: null,

    space: {
      id: 2,
      name: 'Konferencijska dvorana B',
      capacity: 350,
    },

    services: [
      {
        id: 5,
        price_at_booking: 300,
        service: {
          id: 4,
          name: 'Catering',
        },
      },
    ],

    recurring_rule: null,
    created_at: '2026-07-16T09:30:00',
  },

  {
    id: 5,
    event_name: 'Ljetni networking događaj',
    guest_count: 100,

    first_name: 'Luka',
    last_name: 'Milić',
    email: 'luka.milic@example.com',
    phone: '+387 63 999 000',
    company: null,

    start_time: '2026-07-27T18:00:00',
    end_time: '2026-07-27T21:00:00',

    total_price: 580,
    status: 'confirmed',
    notes: 'U slučaju kiše potreban rezervni prostor.',

    google_event_id: 'google-event-5',

    space: {
      id: 5,
      name: 'Vanjski prostor',
      capacity: 180,
    },

    services: [
      {
        id: 6,
        price_at_booking: 100,
        service: {
          id: 2,
          name: 'Ozvučenje',
        },
      },
    ],

    recurring_rule: null,
    created_at: '2026-07-21T11:10:00',
  },
])

const filteredReservations = computed(() => {
  const normalizedSearch = search.value
    .trim()
    .toLowerCase()

  return reservations.value.filter((reservation) => {
    const matchesSearch =
      !normalizedSearch ||
      reservation.event_name
        .toLowerCase()
        .includes(normalizedSearch) ||
      reservation.first_name
        .toLowerCase()
        .includes(normalizedSearch) ||
      reservation.last_name
        .toLowerCase()
        .includes(normalizedSearch) ||
      reservation.email
        .toLowerCase()
        .includes(normalizedSearch) ||
      reservation.space.name
        .toLowerCase()
        .includes(normalizedSearch)

    const matchesStatus =
      selectedStatus.value === 'all' ||
      reservation.status === selectedStatus.value

    const matchesSpace =
      selectedSpace.value === 'all' ||
      Number(reservation.space.id) ===
        Number(selectedSpace.value)

    const reservationDate = new Date(
      reservation.start_time,
    )

    const matchesDateFrom =
      !dateFrom.value ||
      reservationDate >=
        new Date(`${dateFrom.value}T00:00:00`)

    const matchesDateTo =
      !dateTo.value ||
      reservationDate <=
        new Date(`${dateTo.value}T23:59:59`)

    return (
      matchesSearch &&
      matchesStatus &&
      matchesSpace &&
      matchesDateFrom &&
      matchesDateTo
    )
  })
})


const calendarSpaceOptions = computed(() =>
  spaces.map((space) => ({
    title: space.name,
    value: space.id,
  })),
)

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

const calendarHours = computed(() => {
  return Array.from(
    { length: calendarEndHour - calendarStartHour + 1 },
    (_, index) => calendarStartHour + index,
  )
})

const calendarReservations = computed(() => {
  return filteredReservations.value.filter((reservation) => {
    if (reservation.status === 'cancelled') return false

    if (Number(reservation.space.id) !== Number(calendarSpace.value)) {
      return false
    }

    const reservationDate = toDateKey(reservation.start_time)
    return weekDays.value.some((day) => day.key === reservationDate)
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
    (reservation) => toDateKey(reservation.start_time) === dayKey,
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

const statistics = computed(() => {
  const total = reservations.value.length

  const confirmed = reservations.value.filter(
    (reservation) =>
      reservation.status === 'confirmed',
  ).length

  const pending = reservations.value.filter(
    (reservation) =>
      reservation.status === 'pending',
  ).length

  const cancelled = reservations.value.filter(
    (reservation) =>
      reservation.status === 'cancelled',
  ).length

  return {
    total,
    confirmed,
    pending,
    cancelled,
  }
})

const spaceOptions = computed(() => [
  {
    title: 'Svi prostori',
    value: 'all',
  },
  ...spaces.map((space) => ({
    title: space.name,
    value: space.id,
  })),
])

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
  if (!selectedReservation.value) {
    return
  }

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
  return new Intl.DateTimeFormat('hr-HR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(dateValue))
}

function formatTime(dateValue) {
  return new Intl.DateTimeFormat('hr-HR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(dateValue))
}

function formatDateTime(dateValue) {
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
  }).format(value)
}
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
                    {{ reservation.space.name }}
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
                      selectedReservation.space.name
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
                selectedReservation.services.length
              "
              class="services-list"
            >
              <div
                v-for="item in selectedReservation.services"
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

