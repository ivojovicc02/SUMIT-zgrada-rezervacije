<script setup>
import {
  computed,
  onMounted,
  ref,
  watch,
} from 'vue'
import { getReports } from '@/services/reservationService'

const selectedPeriod = ref('year')
const selectedSpace = ref('all')

const isLoading = ref(true)
const errorMessage = ref('')
const lastUpdatedAt = ref(null)

const periodOptions = [
  { value: 'week', label: 'Ovaj tjedan' },
  { value: 'month', label: 'Ovaj mjesec' },
  { value: 'quarter', label: 'Ovo tromjesečje' },
  { value: 'year', label: 'Ova godina' },
]

const spaces = ref([])

const reportStatistics = ref({
  totalReservations: 0,
  totalRevenue: 0,
  averageReservationValue: 0,
  cancelledReservations: 0,
})

const monthlyData = ref([])
const spacePerformance = ref([])
const reservationStatuses = ref([])

const reportGeneratedAt = computed(() => {
  if (!lastUpdatedAt.value) {
    return '—'
  }

  return new Intl.DateTimeFormat('hr-HR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(lastUpdatedAt.value)
})

const selectedPeriodLabel = computed(() => {
  return (
    periodOptions.find(
      (period) => period.value === selectedPeriod.value,
    )?.label || ''
  )
})

const maxReservations = computed(() => {
  if (!monthlyData.value.length) {
    return 0
  }

  return Math.max(
    ...monthlyData.value.map(
      (item) => Number(item.reservations) || 0,
    ),
  )
})

const maxRevenue = computed(() => {
  if (!monthlyData.value.length) {
    return 0
  }

  return Math.max(
    ...monthlyData.value.map(
      (item) => Number(item.revenue) || 0,
    ),
  )
})

const topSpace = computed(() => {
  if (!spacePerformance.value.length) {
    return null
  }

  return [...spacePerformance.value].sort(
    (first, second) =>
      second.reservations - first.reservations,
  )[0]
})

async function loadReports() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await getReports(
      selectedPeriod.value,
      selectedSpace.value,
    )

    const data = response.data

    reportStatistics.value = {
      totalReservations:
        data.statistics?.totalReservations ?? 0,
      totalRevenue:
        data.statistics?.totalRevenue ?? 0,
      averageReservationValue:
        data.statistics?.averageReservationValue ?? 0,
      cancelledReservations:
        data.statistics?.cancelledReservations ?? 0,
    }

    monthlyData.value = Array.isArray(data.monthlyData)
      ? data.monthlyData
      : []

    spacePerformance.value = Array.isArray(
      data.spacePerformance,
    )
      ? data.spacePerformance
      : []

    reservationStatuses.value = Array.isArray(
      data.reservationStatuses,
    )
      ? data.reservationStatuses
      : []

    if (selectedSpace.value === 'all') {
      spaces.value = Array.isArray(data.spaces)
        ? data.spaces
        : []
    }

    lastUpdatedAt.value = new Date()
  } catch (error) {
    console.error(
      'Greška pri dohvaćanju izvještaja:',
      error,
    )

    errorMessage.value =
      error.response?.data?.detail ||
      'Nije moguće učitati izvještaj.'
  } finally {
    isLoading.value = false
  }
}

function getReservationBarHeight(value) {
  if (!maxReservations.value) {
    return 0
  }

  return Math.max(
    4,
    (Number(value) / maxReservations.value) * 100,
  )
}

function getRevenueBarHeight(value) {
  if (!maxRevenue.value) {
    return 0
  }

  return Math.max(
    4,
    (Number(value) / maxRevenue.value) * 100,
  )
}

function formatCurrency(value) {
  return new Intl.NumberFormat('hr-HR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(Number(value) || 0)
}

function formatNumber(value) {
  return new Intl.NumberFormat('hr-HR').format(
    Number(value) || 0,
  )
}

function getStatusIcon(status) {
  const icons = {
    pending: '…',
    confirmed: '✓',
    completed: '✓',
    cancelled: '✕',
  }

  return icons[status] || '•'
}

watch(
  [selectedPeriod, selectedSpace],
  () => {
    loadReports()
  },
)

onMounted(() => {
  loadReports()
})
</script>

<template>
  <section class="reports-page">
    <header class="reports-header">
      <div>
        <p class="reports-eyebrow">
          Analitika
        </p>

        <h1>Izvještaji i statistika</h1>

        <p class="reports-description">
          Pregled rezervacija i prihoda prema
          odabranom razdoblju i prostoru.
        </p>
      </div>

      <button
        type="button"
        class="refresh-button"
        :disabled="isLoading"
        @click="loadReports"
      >
        Osvježi podatke
      </button>
    </header>

    <section class="filters-card">
      <div class="filter-group">
        <label for="report-period">
          Razdoblje
        </label>

        <select
          id="report-period"
          v-model="selectedPeriod"
          :disabled="isLoading"
        >
          <option
            v-for="period in periodOptions"
            :key="period.value"
            :value="period.value"
          >
            {{ period.label }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label for="report-space">
          Prostor
        </label>

        <select
          id="report-space"
          v-model="selectedSpace"
          :disabled="isLoading"
        >
          <option value="all">
            Svi prostori
          </option>

          <option
            v-for="space in spaces"
            :key="space.id"
            :value="space.id"
          >
            {{ space.name }}
          </option>
        </select>
      </div>

      <div class="filter-summary">
        <span>Prikazani podaci</span>

        <strong>
          {{ selectedPeriodLabel }}
        </strong>
      </div>

      <div class="generated-at">
        <span>Posljednje ažuriranje</span>

        <strong>
          {{ reportGeneratedAt }}
        </strong>
      </div>
    </section>

    <div
      v-if="errorMessage"
      class="error-box"
    >
      <div>
        <strong>Greška pri učitavanju</strong>
        <p>{{ errorMessage }}</p>
      </div>

      <button
        type="button"
        @click="loadReports"
      >
        Pokušaj ponovno
      </button>
    </div>

    <div
      v-if="isLoading"
      class="loading-state"
    >
      <span class="spinner"></span>
      <p>Učitavanje izvještaja...</p>
    </div>

    <template v-else>
      <div class="statistics-grid">
        <article class="stat-card">
          <div class="stat-card__header">
            <span class="stat-icon">📅</span>
            <span class="stat-badge">
              {{ selectedPeriodLabel }}
            </span>
          </div>

          <span class="stat-label">
            Ukupno rezervacija
          </span>

          <strong>
            {{
              formatNumber(
                reportStatistics.totalReservations,
              )
            }}
          </strong>

          <p>
            Rezervacije u odabranom razdoblju
          </p>
        </article>

        <article class="stat-card">
          <div class="stat-card__header">
            <span class="stat-icon">💰</span>
            <span class="stat-badge">
              Potvrđene i završene
            </span>
          </div>

          <span class="stat-label">
            Ukupan prihod
          </span>

          <strong>
            {{
              formatCurrency(
                reportStatistics.totalRevenue,
              )
            }}
            KM
          </strong>

          <p>
            Zbroj vrijednosti obračunatih rezervacija
          </p>
        </article>

        <article class="stat-card">
          <div class="stat-card__header">
            <span class="stat-icon">📈</span>
            <span class="stat-badge">
              Prosjek
            </span>
          </div>

          <span class="stat-label">
            Prosječna vrijednost
          </span>

          <strong>
            {{
              formatCurrency(
                reportStatistics
                  .averageReservationValue,
              )
            }}
            KM
          </strong>

          <p>
            Prosječan prihod po obračunatoj rezervaciji
          </p>
        </article>

        <article class="stat-card">
          <div class="stat-card__header">
            <span class="stat-icon">✕</span>
            <span class="stat-badge stat-badge--danger">
              Otkazane
            </span>
          </div>

          <span class="stat-label">
            Otkazane rezervacije
          </span>

          <strong>
            {{
              formatNumber(
                reportStatistics
                  .cancelledReservations,
              )
            }}
          </strong>

          <p>
            Broj otkazanih rezervacija u razdoblju
          </p>
        </article>
      </div>

      <div class="reports-main-grid">
        <article class="report-card chart-card">
          <div class="card-header">
            <div>
              <h2>Rezervacije po mjesecima</h2>

              <p>
                Broj evidentiranih rezervacija
              </p>
            </div>

            <span class="card-summary">
              {{ reportStatistics.totalReservations }}
              ukupno
            </span>
          </div>

          <div
            v-if="monthlyData.length"
            class="bar-chart"
            :style="{
              gridTemplateColumns: `repeat(${monthlyData.length}, minmax(35px, 1fr))`,
            }"
          >
            <div
              v-for="item in monthlyData"
              :key="`${item.fullMonth}-${item.month}`"
              class="bar-chart__column"
            >
              <div class="bar-chart__area">
                <span class="bar-tooltip">
                  {{ item.reservations }} rezervacija
                </span>

                <div
                  class="bar bar--reservations"
                  :style="{
                    height: `${getReservationBarHeight(
                      item.reservations,
                    )}%`,
                  }"
                ></div>
              </div>

              <span
                class="bar-label"
                :title="item.fullMonth"
              >
                {{ item.month }}
              </span>
            </div>
          </div>

          <div
            v-else
            class="empty-state"
          >
            Nema podataka za odabrano razdoblje.
          </div>
        </article>

        <article class="report-card overview-card">
          <div class="card-header">
            <div>
              <h2>Najuspješniji prostor</h2>

              <p>
                Prostor s najviše rezervacija
              </p>
            </div>

            <span
              v-if="topSpace"
              class="rank-badge"
            >
              #1
            </span>
          </div>

          <template v-if="topSpace">
            <div class="top-space">
              <span class="top-space__icon">
                🏆
              </span>

              <h3>
                {{ topSpace.name }}
              </h3>
            </div>

            <div class="top-space__statistics">
              <div>
                <span>Rezervacije</span>

                <strong>
                  {{ topSpace.reservations }}
                </strong>
              </div>

              <div>
                <span>Prihod</span>

                <strong>
                  {{
                    formatCurrency(
                      topSpace.revenue,
                    )
                  }}
                  KM
                </strong>
              </div>

              <div>
                <span>Otkazane</span>

                <strong>
                  {{
                    topSpace.cancelledReservations
                  }}
                </strong>
              </div>
            </div>
          </template>

          <div
            v-else
            class="empty-state"
          >
            Nema podataka o prostorima.
          </div>
        </article>
      </div>

      <article class="report-card chart-card">
        <div class="card-header">
          <div>
            <h2>Prihod po mjesecima</h2>

            <p>
              Prihod potvrđenih i završenih rezervacija
            </p>
          </div>

          <span class="card-summary">
            {{
              formatCurrency(
                reportStatistics.totalRevenue,
              )
            }}
            KM
          </span>
        </div>

        <div
          v-if="monthlyData.length"
          class="bar-chart"
          :style="{
            gridTemplateColumns: `repeat(${monthlyData.length}, minmax(35px, 1fr))`,
          }"
        >
          <div
            v-for="item in monthlyData"
            :key="`revenue-${item.fullMonth}-${item.month}`"
            class="bar-chart__column"
          >
            <div class="bar-chart__area">
              <span class="bar-tooltip">
                {{ formatCurrency(item.revenue) }}
                KM
              </span>

              <div
                class="bar bar--revenue"
                :style="{
                  height: `${getRevenueBarHeight(
                    item.revenue,
                  )}%`,
                }"
              ></div>
            </div>

            <span
              class="bar-label"
              :title="item.fullMonth"
            >
              {{ item.month }}
            </span>
          </div>
        </div>

        <div
          v-else
          class="empty-state"
        >
          Nema podataka o prihodima.
        </div>
      </article>

      <article class="report-card">
        <div class="card-header">
          <div>
            <h2>Uspješnost prostora</h2>

            <p>
              Usporedba broja rezervacija i prihoda
            </p>
          </div>

          <span class="card-summary">
            {{ spacePerformance.length }}
            prostora
          </span>
        </div>

        <div
          v-if="spacePerformance.length"
          class="table-wrapper"
        >
          <table class="performance-table">
            <thead>
              <tr>
                <th>Prostor</th>
                <th>Rezervacije</th>
                <th>Prihod</th>
                <th>Otkazane</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="space in spacePerformance"
                :key="space.id"
              >
                <td>
                  <strong>
                    {{ space.name }}
                  </strong>
                </td>

                <td>
                  <strong>
                    {{ space.reservations }}
                  </strong>
                </td>

                <td>
                  <strong>
                    {{
                      formatCurrency(
                        space.revenue,
                      )
                    }}
                    KM
                  </strong>
                </td>

                <td>
                  <strong>
                    {{
                      space.cancelledReservations
                    }}
                  </strong>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-else
          class="empty-state"
        >
          Nema podataka o prostorima.
        </div>
      </article>

      <article class="report-card">
        <div class="card-header">
          <div>
            <h2>Status rezervacija</h2>

            <p>
              Raspodjela rezervacija prema statusu
            </p>
          </div>
        </div>

        <div
          v-if="reservationStatuses.length"
          class="status-list"
        >
          <div
            v-for="item in reservationStatuses"
            :key="item.status"
            class="status-item"
          >
            <div
              class="status-icon"
              :class="`status-icon--${item.status}`"
            >
              {{ getStatusIcon(item.status) }}
            </div>

            <div class="status-content">
              <strong>
                {{ item.label }}
              </strong>

              <span>
                {{ item.percentage }}% rezervacija
              </span>
            </div>

            <strong class="status-count">
              {{ item.count }}
            </strong>
          </div>
        </div>

        <div
          v-else
          class="empty-state"
        >
          Nema podataka o statusima.
        </div>
      </article>
    </template>
  </section>
</template>

<style scoped>
.reports-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.reports-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.reports-eyebrow {
  margin: 0 0 6px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.reports-header h1 {
  margin: 0;
  color: #0f172a;
  font-size: clamp(26px, 3vw, 36px);
}

.reports-description {
  margin: 8px 0 0;
  color: #64748b;
}

.refresh-button,
.error-box button {
  padding: 11px 16px;
  border: 0;
  border-radius: 10px;
  background: #2563eb;
  color: white;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.refresh-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.filters-card {
  display: grid;
  grid-template-columns:
    minmax(180px, 240px)
    minmax(200px, 280px)
    minmax(180px, 1fr)
    auto;
  align-items: end;
  gap: 18px;
  padding: 18px 20px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  background: white;
  box-shadow: 0 8px 24px rgb(15 23 42 / 4%);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.filter-group label {
  color: #475569;
  font-size: 13px;
  font-weight: 700;
}

.filter-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 9px;
  background: white;
  color: #0f172a;
  font: inherit;
}

.filter-summary,
.generated-at {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-bottom: 3px;
}

.filter-summary span,
.generated-at span {
  color: #94a3b8;
  font-size: 12px;
}

.filter-summary strong,
.generated-at strong {
  color: #334155;
  font-size: 13px;
}

.generated-at {
  text-align: right;
}

.error-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 18px;
  border: 1px solid #fecdd3;
  border-radius: 14px;
  background: #fff1f2;
  color: #9f1239;
}

.error-box p {
  margin: 4px 0 0;
  font-size: 13px;
}

.error-box button {
  flex-shrink: 0;
  padding: 9px 13px;
  background: #be123c;
  font-size: 13px;
}

.loading-state {
  display: grid;
  min-height: 300px;
  place-items: center;
  align-content: center;
  gap: 14px;
  color: #64748b;
}

.loading-state p {
  margin: 0;
}

.spinner {
  width: 38px;
  height: 38px;
  border: 4px solid #dbeafe;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.statistics-grid {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card,
.report-card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: white;
  box-shadow: 0 8px 24px rgb(15 23 42 / 5%);
}

.stat-card {
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.stat-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 18px;
}

.stat-icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 12px;
  background: #eff6ff;
  font-size: 20px;
}

.stat-badge,
.card-summary,
.rank-badge {
  padding: 5px 9px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 11px;
  font-weight: 700;
}

.stat-badge--danger {
  background: #fff1f2;
  color: #be123c;
}

.stat-label {
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.stat-card > strong {
  margin-top: 7px;
  color: #0f172a;
  font-size: 28px;
}

.stat-card p {
  margin: 7px 0 0;
  color: #94a3b8;
  font-size: 12px;
}

.reports-main-grid {
  display: grid;
  grid-template-columns:
    minmax(0, 1.65fr)
    minmax(300px, 0.75fr);
  gap: 20px;
}

.report-card {
  padding: 22px;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.card-header h2 {
  margin: 0;
  color: #0f172a;
  font-size: 19px;
}

.card-header p {
  margin: 5px 0 0;
  color: #94a3b8;
  font-size: 13px;
}

.bar-chart {
  display: grid;
  align-items: end;
  gap: 10px;
  min-height: 270px;
  overflow-x: auto;
  padding: 18px 8px 0;
  border-bottom: 1px solid #e2e8f0;
  background-image: repeating-linear-gradient(
    to bottom,
    transparent,
    transparent 54px,
    #f1f5f9 55px
  );
}

.bar-chart__column {
  display: flex;
  height: 250px;
  min-width: 35px;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  gap: 9px;
}

.bar-chart__area {
  position: relative;
  display: flex;
  width: 100%;
  height: 220px;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: min(34px, 75%);
  min-height: 4px;
  border-radius: 7px 7px 2px 2px;
}

.bar--reservations {
  background: linear-gradient(
    180deg,
    #3b82f6,
    #2563eb
  );
}

.bar--revenue {
  background: linear-gradient(
    180deg,
    #10b981,
    #059669
  );
}

.bar-tooltip {
  position: absolute;
  top: -20px;
  z-index: 2;
  display: none;
  padding: 6px 8px;
  border-radius: 7px;
  background: #0f172a;
  color: white;
  font-size: 10px;
  white-space: nowrap;
}

.bar-chart__column:hover .bar-tooltip {
  display: block;
}

.bar-label {
  color: #64748b;
  font-size: 11px;
  font-weight: 600;
}

.top-space {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0 22px;
  text-align: center;
}

.top-space__icon {
  display: grid;
  width: 64px;
  height: 64px;
  place-items: center;
  border-radius: 18px;
  background: #fffbeb;
  font-size: 30px;
}

.top-space h3 {
  margin: 14px 0 0;
  color: #0f172a;
  font-size: 18px;
}

.top-space__statistics {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.top-space__statistics div {
  padding: 12px 7px;
  border-radius: 10px;
  background: #f8fafc;
  text-align: center;
}

.top-space__statistics span,
.top-space__statistics strong {
  display: block;
}

.top-space__statistics span {
  color: #94a3b8;
  font-size: 10px;
}

.top-space__statistics strong {
  margin-top: 5px;
  color: #0f172a;
  font-size: 13px;
}

.table-wrapper {
  overflow-x: auto;
}

.performance-table {
  width: 100%;
  border-collapse: collapse;
}

.performance-table th {
  padding: 0 12px 12px;
  border-bottom: 1px solid #e2e8f0;
  color: #94a3b8;
  font-size: 11px;
  text-align: left;
  text-transform: uppercase;
}

.performance-table td {
  min-width: 120px;
  padding: 15px 12px;
  border-bottom: 1px solid #f1f5f9;
  color: #64748b;
  font-size: 13px;
}

.performance-table td:first-child {
  min-width: 210px;
}

.performance-table tbody tr:last-child td {
  border-bottom: 0;
}

.performance-table td strong {
  color: #0f172a;
}

.status-list {
  display: flex;
  flex-direction: column;
}

.status-item {
  display: grid;
  grid-template-columns:
    auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 13px 0;
  border-bottom: 1px solid #f1f5f9;
}

.status-item:last-child {
  border-bottom: 0;
}

.status-icon {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 10px;
  font-weight: 800;
}

.status-icon--pending {
  background: #fffbeb;
  color: #b45309;
}

.status-icon--confirmed,
.status-icon--completed {
  background: #ecfdf5;
  color: #047857;
}

.status-icon--cancelled {
  background: #fff1f2;
  color: #be123c;
}

.status-content strong,
.status-content span {
  display: block;
}

.status-content strong {
  color: #0f172a;
  font-size: 13px;
}

.status-content span {
  margin-top: 4px;
  color: #94a3b8;
  font-size: 11px;
}

.status-count {
  color: #0f172a;
  font-size: 16px;
}

.empty-state {
  display: grid;
  min-height: 180px;
  place-items: center;
  color: #94a3b8;
  text-align: center;
}

@media (max-width: 1200px) {
  .statistics-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .filters-card {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .generated-at {
    text-align: left;
  }
}

@media (max-width: 960px) {
  .reports-main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .reports-header,
  .error-box {
    flex-direction: column;
  }

  .refresh-button,
  .error-box button {
    width: 100%;
  }

  .filters-card,
  .statistics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .report-card,
  .stat-card {
    padding: 17px;
  }

  .top-space__statistics {
    grid-template-columns: 1fr;
  }
}
</style>
