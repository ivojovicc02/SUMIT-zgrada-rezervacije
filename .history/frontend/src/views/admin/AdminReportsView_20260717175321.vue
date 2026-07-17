<script setup>
import { computed, ref } from 'vue'

const selectedPeriod = ref('year')
const selectedSpace = ref('all')

const periodOptions = [
  {
    value: 'week',
    label: 'Ovaj tjedan',
  },
  {
    value: 'month',
    label: 'Ovaj mjesec',
  },
  {
    value: 'quarter',
    label: 'Ovo tromjesečje',
  },
  {
    value: 'year',
    label: 'Ova godina',
  },
]

const spaces = ref([
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
])

const reportStatistics = ref({
  totalReservations: 384,
  totalRevenue: 28450,
  averageReservationValue: 74.09,
  occupancyRate: 68,
  cancelledReservations: 22,
  totalGuests: 4876,
})

const monthlyData = ref([
  {
    month: 'Sij',
    fullMonth: 'Siječanj',
    reservations: 24,
    revenue: 1650,
  },
  {
    month: 'Velj',
    fullMonth: 'Veljača',
    reservations: 29,
    revenue: 1950,
  },
  {
    month: 'Ožu',
    fullMonth: 'Ožujak',
    reservations: 35,
    revenue: 2380,
  },
  {
    month: 'Tra',
    fullMonth: 'Travanj',
    reservations: 31,
    revenue: 2210,
  },
  {
    month: 'Svi',
    fullMonth: 'Svibanj',
    reservations: 42,
    revenue: 3150,
  },
  {
    month: 'Lip',
    fullMonth: 'Lipanj',
    reservations: 46,
    revenue: 3480,
  },
  {
    month: 'Srp',
    fullMonth: 'Srpanj',
    reservations: 38,
    revenue: 2980,
  },
  {
    month: 'Kol',
    fullMonth: 'Kolovoz',
    reservations: 25,
    revenue: 1820,
  },
  {
    month: 'Ruj',
    fullMonth: 'Rujan',
    reservations: 33,
    revenue: 2450,
  },
  {
    month: 'Lis',
    fullMonth: 'Listopad',
    reservations: 36,
    revenue: 2760,
  },
  {
    month: 'Stu',
    fullMonth: 'Studeni',
    reservations: 27,
    revenue: 1930,
  },
  {
    month: 'Pro',
    fullMonth: 'Prosinac',
    reservations: 18,
    revenue: 1690,
  },
])

const spacePerformance = ref([
  {
    id: 1,
    name: 'Konferencijska dvorana A',
    category: 'Konferencijske dvorane',
    reservations: 96,
    revenue: 9840,
    occupancy: 87,
  },
  {
    id: 2,
    name: 'Multimedijalna dvorana',
    category: 'Konferencijske dvorane',
    reservations: 78,
    revenue: 7210,
    occupancy: 74,
  },
  {
    id: 3,
    name: 'Konferencijska dvorana B',
    category: 'Konferencijske dvorane',
    reservations: 65,
    revenue: 5480,
    occupancy: 68,
  },
  {
    id: 4,
    name: 'Ured 204',
    category: 'Uredi',
    reservations: 58,
    revenue: 3240,
    occupancy: 59,
  },
  {
    id: 5,
    name: 'Vanjski prostor',
    category: 'Vanjski prostori',
    reservations: 34,
    revenue: 2680,
    occupancy: 42,
  },
  {
    id: 6,
    name: 'Ured 102',
    category: 'Uredi',
    reservations: 29,
    revenue: 0,
    occupancy: 36,
  },
])

const categoryData = ref([
  {
    name: 'Konferencijske dvorane',
    reservations: 239,
    percentage: 62,
  },
  {
    name: 'Uredi i radni prostori',
    reservations: 111,
    percentage: 29,
  },
  {
    name: 'Vanjski prostori',
    reservations: 34,
    percentage: 9,
  },
])

const reservationStatuses = ref([
  {
    status: 'confirmed',
    label: 'Potvrđene',
    count: 332,
    percentage: 86,
  },
  {
    status: 'completed',
    label: 'Završene',
    count: 210,
    percentage: 55,
  },
  {
    status: 'cancelled',
    label: 'Otkazane',
    count: 22,
    percentage: 6,
  },
  {
    status: 'upcoming',
    label: 'Nadolazeće',
    count: 152,
    percentage: 39,
  },
])

const popularServices = ref([
  {
    id: 1,
    name: 'Projektor',
    uses: 168,
    revenue: 1680,
  },
  {
    id: 2,
    name: 'Ozvučenje',
    uses: 104,
    revenue: 2080,
  },
  {
    id: 3,
    name: 'Catering',
    uses: 78,
    revenue: 4680,
  },
  {
    id: 4,
    name: 'Tehnička podrška',
    uses: 64,
    revenue: 1920,
  },
  {
    id: 5,
    name: 'Dodatni stolovi i stolice',
    uses: 53,
    revenue: 795,
  },
])

const reportGeneratedAt = computed(() => {
  return new Intl.DateTimeFormat('hr-HR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date())
})

const selectedPeriodLabel = computed(() => {
  return periodOptions.find(
    (period) => period.value === selectedPeriod.value,
  )?.label || ''
})

const maxReservations = computed(() => {
  return Math.max(
    ...monthlyData.value.map(
      (item) => item.reservations,
    ),
  )
})

const maxRevenue = computed(() => {
  return Math.max(
    ...monthlyData.value.map(
      (item) => item.revenue,
    ),
  )
})

const filteredSpacePerformance = computed(() => {
  if (selectedSpace.value === 'all') {
    return spacePerformance.value
  }

  return spacePerformance.value.filter(
    (space) =>
      Number(space.id) ===
      Number(selectedSpace.value),
  )
})

const topSpace = computed(() => {
  return [...spacePerformance.value].sort(
    (first, second) =>
      second.reservations - first.reservations,
  )[0]
})

function getReservationBarHeight(value) {
  if (!maxReservations.value) {
    return 0
  }

  return Math.max(
    4,
    (value / maxReservations.value) * 100,
  )
}

function getRevenueBarHeight(value) {
  if (!maxRevenue.value) {
    return 0
  }

  return Math.max(
    4,
    (value / maxRevenue.value) * 100,
  )
}

function formatCurrency(value) {
  return new Intl.NumberFormat('hr-HR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)
}

function formatNumber(value) {
  return new Intl.NumberFormat('hr-HR').format(
    value,
  )
}

function getOccupancyClass(occupancy) {
  if (occupancy >= 75) {
    return 'occupancy--high'
  }

  if (occupancy >= 50) {
    return 'occupancy--medium'
  }

  return 'occupancy--low'
}

function exportReport() {
  window.alert(
    'Izvoz izvještaja bit će povezan s backendom naknadno.',
  )
}
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
          Detaljan pregled rezervacija, prihoda i
          iskorištenosti prostora.
        </p>
      </div>

      <button
        type="button"
        class="export-button"
        @click="exportReport"
      >
        <span>↓</span>
        Izvezi izvještaj
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
        <span>Prikazani podaci:</span>

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

    <div class="statistics-grid">
      <article class="stat-card">
        <div class="stat-card__header">
          <span class="stat-icon">
            📅
          </span>

          <span class="trend-badge trend-badge--positive">
            +14,2%
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
          U odnosu na prethodno razdoblje
        </p>
      </article>

      <article class="stat-card">
        <div class="stat-card__header">
          <span class="stat-icon">
            💰
          </span>

          <span class="trend-badge trend-badge--positive">
            +9,8%
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
          Prihod od rezervacija i usluga
        </p>
      </article>

      <article class="stat-card">
        <div class="stat-card__header">
          <span class="stat-icon">
            📈
          </span>

          <span class="trend-badge">
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
          Prosječan prihod po rezervaciji
        </p>
      </article>

      <article class="stat-card">
        <div class="stat-card__header">
          <span class="stat-icon">
            🏢
          </span>

          <span class="trend-badge trend-badge--positive">
            +5,4%
          </span>
        </div>

        <span class="stat-label">
          Iskorištenost prostora
        </span>

        <strong>
          {{ reportStatistics.occupancyRate }}%
        </strong>

        <p>
          Prosječna zauzetost svih prostora
        </p>
      </article>

      <article class="stat-card">
        <div class="stat-card__header">
          <span class="stat-icon">
            👥
          </span>

          <span class="trend-badge trend-badge--positive">
            +18%
          </span>
        </div>

        <span class="stat-label">
          Ukupan broj gostiju
        </span>

        <strong>
          {{
            formatNumber(
              reportStatistics.totalGuests,
            )
          }}
        </strong>

        <p>
          Posjetitelji svih događaja
        </p>
      </article>

      <article class="stat-card">
        <div class="stat-card__header">
          <span class="stat-icon">
            ✕
          </span>

          <span class="trend-badge trend-badge--negative">
            5,7%
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
          Udio otkazivanja u rezervacijama
        </p>
      </article>
    </div>

    <div class="reports-main-grid">
      <article class="report-card chart-card">
        <div class="card-header">
          <div>
            <h2>Rezervacije po mjesecima</h2>

            <p>
              Broj evidentiranih rezervacija tijekom
              godine
            </p>
          </div>

          <span class="card-summary">
            {{ reportStatistics.totalReservations }}
            ukupno
          </span>
        </div>

        <div class="bar-chart">
          <div
            v-for="item in monthlyData"
            :key="item.month"
            class="bar-chart__column"
          >
            <div class="bar-chart__area">
              <span class="bar-tooltip">
                {{ item.reservations }}
                rezervacija
              </span>

              <div
                class="bar bar--reservations"
                :style="{
                  height: `${
                    getReservationBarHeight(
                      item.reservations,
                    )
                  }%`,
                }"
              ></div>
            </div>

            <span class="bar-label">
              {{ item.month }}
            </span>
          </div>
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

          <span class="rank-badge">
            #1
          </span>
        </div>

        <div class="top-space">
          <span class="top-space__icon">
            🏆
          </span>

          <h3>
            {{ topSpace.name }}
          </h3>

          <p>
            {{ topSpace.category }}
          </p>
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
              {{ formatCurrency(topSpace.revenue) }}
              KM
            </strong>
          </div>

          <div>
            <span>Zauzetost</span>

            <strong>
              {{ topSpace.occupancy }}%
            </strong>
          </div>
        </div>

        <div class="occupancy-progress">
          <div class="occupancy-progress__header">
            <span>Iskorištenost kapaciteta</span>

            <strong>
              {{ topSpace.occupancy }}%
            </strong>
          </div>

          <div class="progress-track">
            <div
              class="progress-value"
              :style="{
                width: `${topSpace.occupancy}%`,
              }"
            ></div>
          </div>
        </div>
      </article>
    </div>

    <div class="reports-main-grid">
      <article class="report-card chart-card">
        <div class="card-header">
          <div>
            <h2>Prihod po mjesecima</h2>

            <p>
              Ukupan ostvareni prihod u KM
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

        <div class="bar-chart">
          <div
            v-for="item in monthlyData"
            :key="item.month"
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
                  height: `${
                    getRevenueBarHeight(
                      item.revenue,
                    )
                  }%`,
                }"
              ></div>
            </div>

            <span class="bar-label">
              {{ item.month }}
            </span>
          </div>
        </div>
      </article>

      <article class="report-card">
        <div class="card-header">
          <div>
            <h2>Rezervacije po kategoriji</h2>

            <p>
              Raspodjela ukupnih rezervacija
            </p>
          </div>
        </div>

        <div class="category-list">
          <div
            v-for="category in categoryData"
            :key="category.name"
            class="category-item"
          >
            <div class="category-item__header">
              <div>
                <strong>
                  {{ category.name }}
                </strong>

                <span>
                  {{ category.reservations }}
                  rezervacija
                </span>
              </div>

              <strong>
                {{ category.percentage }}%
              </strong>
            </div>

            <div class="category-track">
              <div
                class="category-value"
                :style="{
                  width: `${category.percentage}%`,
                }"
              ></div>
            </div>
          </div>
        </div>
      </article>
    </div>

    <article class="report-card">
      <div class="card-header">
        <div>
          <h2>Uspješnost prostora</h2>

          <p>
            Usporedba rezervacija, prihoda i
            iskorištenosti
          </p>
        </div>

        <span class="card-summary">
          {{ filteredSpacePerformance.length }}
          prostora
        </span>
      </div>

      <div class="table-wrapper">
        <table class="performance-table">
          <thead>
            <tr>
              <th>Prostor</th>
              <th>Kategorija</th>
              <th>Rezervacije</th>
              <th>Prihod</th>
              <th>Iskorištenost</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="space in filteredSpacePerformance"
              :key="space.id"
            >
              <td>
                <strong>
                  {{ space.name }}
                </strong>
              </td>

              <td>
                {{ space.category }}
              </td>

              <td>
                <strong>
                  {{ space.reservations }}
                </strong>
              </td>

              <td>
                <strong>
                  {{ formatCurrency(space.revenue) }}
                  KM
                </strong>
              </td>

              <td>
                <div class="table-occupancy">
                  <div class="table-occupancy__top">
                    <span>
                      {{ space.occupancy }}%
                    </span>

                    <span
                      class="occupancy-label"
                      :class="
                        getOccupancyClass(
                          space.occupancy,
                        )
                      "
                    >
                      {{
                        space.occupancy >= 75
                          ? 'Visoka'
                          : space.occupancy >= 50
                            ? 'Srednja'
                            : 'Niska'
                      }}
                    </span>
                  </div>

                  <div class="table-progress">
                    <div
                      class="table-progress__value"
                      :class="
                        getOccupancyClass(
                          space.occupancy,
                        )
                      "
                      :style="{
                        width: `${space.occupancy}%`,
                      }"
                    ></div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <div class="reports-bottom-grid">
      <article class="report-card">
        <div class="card-header">
          <div>
            <h2>Status rezervacija</h2>

            <p>
              Trenutno stanje rezervacija
            </p>
          </div>
        </div>

        <div class="status-list">
          <div
            v-for="item in reservationStatuses"
            :key="item.status"
            class="status-item"
          >
            <div
              class="status-icon"
              :class="`status-icon--${item.status}`"
            >
              <span v-if="item.status === 'confirmed'">
                ✓
              </span>

              <span v-else-if="item.status === 'completed'">
                ✓
              </span>

              <span v-else-if="item.status === 'cancelled'">
                ✕
              </span>

              <span v-else>
                →
              </span>
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
      </article>

      <article class="report-card">
        <div class="card-header">
          <div>
            <h2>Najčešće dodatne usluge</h2>

            <p>
              Usluge odabrane uz rezervacije
            </p>
          </div>
        </div>

        <div class="services-list">
          <div
            v-for="(service, index) in popularServices"
            :key="service.id"
            class="service-item"
          >
            <span class="service-rank">
              {{ index + 1 }}
            </span>

            <div class="service-content">
              <strong>
                {{ service.name }}
              </strong>

              <span>
                Odabrano {{ service.uses }} puta
              </span>
            </div>

            <div class="service-revenue">
              <strong>
                {{ formatCurrency(service.revenue) }}
                KM
              </strong>

              <span>
                prihod
              </span>
            </div>
          </div>
        </div>
      </article>
    </div>
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

.export-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 16px;
  border: 0;
  border-radius: 10px;
  background: #2563eb;
  color: white;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  transition:
    background 0.2s ease,
    transform 0.2s ease;
}

.export-button:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
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

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(
    3,
    minmax(0, 1fr)
  );
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
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 30px rgb(15 23 42 / 9%);
}

.stat-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.trend-badge,
.card-summary,
.rank-badge {
  padding: 5px 9px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 11px;
  font-weight: 700;
}

.trend-badge--positive {
  background: #ecfdf5;
  color: #047857;
}

.trend-badge--negative {
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

.reports-bottom-grid {
  display: grid;
  grid-template-columns: repeat(
    2,
    minmax(0, 1fr)
  );
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
  grid-template-columns: repeat(
    12,
    minmax(28px, 1fr)
  );
  align-items: end;
  gap: 10px;
  min-height: 270px;
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
  transition:
    height 0.4s ease,
    opacity 0.2s ease;
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

.bar-chart__column:hover .bar {
  opacity: 0.8;
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

.top-space p {
  margin: 5px 0 0;
  color: #94a3b8;
  font-size: 13px;
}

.top-space__statistics {
  display: grid;
  grid-template-columns: repeat(
    3,
    minmax(0, 1fr)
  );
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

.occupancy-progress {
  margin-top: 20px;
}

.occupancy-progress__header {
  display: flex;
  justify-content: space-between;
  color: #64748b;
  font-size: 12px;
}

.occupancy-progress__header strong {
  color: #0f172a;
}

.progress-track,
.category-track,
.table-progress {
  overflow: hidden;
  border-radius: 999px;
  background: #e2e8f0;
}

.progress-track {
  height: 9px;
  margin-top: 9px;
}

.progress-value {
  height: 100%;
  border-radius: inherit;
  background: #2563eb;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 21px;
}

.category-item__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.category-item__header strong,
.category-item__header span {
  display: block;
}

.category-item__header strong {
  color: #0f172a;
  font-size: 13px;
}

.category-item__header span {
  margin-top: 4px;
  color: #94a3b8;
  font-size: 11px;
}

.category-track {
  height: 8px;
  margin-top: 10px;
}

.category-value {
  height: 100%;
  border-radius: inherit;
  background: #2563eb;
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
  min-width: 110px;
  padding: 15px 12px;
  border-bottom: 1px solid #f1f5f9;
  color: #64748b;
  font-size: 13px;
}

.performance-table tbody tr:last-child td {
  border-bottom: 0;
}

.performance-table td:first-child {
  min-width: 210px;
}

.performance-table td strong {
  color: #0f172a;
}

.table-occupancy {
  min-width: 170px;
}

.table-occupancy__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.occupancy-label {
  padding: 4px 7px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
}

.table-progress {
  height: 6px;
  margin-top: 8px;
}

.table-progress__value {
  height: 100%;
  border-radius: inherit;
}

.occupancy--high {
  background: #d1fae5;
  color: #047857;
}

.table-progress__value.occupancy--high {
  background: #10b981;
}

.occupancy--medium {
  background: #fef3c7;
  color: #b45309;
}

.table-progress__value.occupancy--medium {
  background: #f59e0b;
}

.occupancy--low {
  background: #fee2e2;
  color: #b91c1c;
}

.table-progress__value.occupancy--low {
  background: #ef4444;
}

.status-list,
.services-list {
  display: flex;
  flex-direction: column;
}

.status-item,
.service-item {
  display: grid;
  align-items: center;
  gap: 12px;
  padding: 13px 0;
  border-bottom: 1px solid #f1f5f9;
}

.status-item {
  grid-template-columns: auto minmax(0, 1fr) auto;
}

.service-item {
  grid-template-columns: auto minmax(0, 1fr) auto;
}

.status-item:last-child,
.service-item:last-child {
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

.status-icon--confirmed,
.status-icon--completed {
  background: #ecfdf5;
  color: #047857;
}

.status-icon--cancelled {
  background: #fff1f2;
  color: #be123c;
}

.status-icon--upcoming {
  background: #eff6ff;
  color: #1d4ed8;
}

.status-content strong,
.status-content span,
.service-content strong,
.service-content span,
.service-revenue strong,
.service-revenue span {
  display: block;
}

.status-content strong,
.service-content strong {
  color: #0f172a;
  font-size: 13px;
}

.status-content span,
.service-content span {
  margin-top: 4px;
  color: #94a3b8;
  font-size: 11px;
}

.status-count {
  color: #0f172a;
  font-size: 16px;
}

.service-rank {
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  border-radius: 8px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
  font-weight: 800;
}

.service-revenue {
  text-align: right;
}

.service-revenue strong {
  color: #0f172a;
  font-size: 12px;
}

.service-revenue span {
  margin-top: 3px;
  color: #94a3b8;
  font-size: 10px;
}

@media (max-width: 1200px) {
  .statistics-grid {
    grid-template-columns: repeat(
      2,
      minmax(0, 1fr)
    );
  }

  .filters-card {
    grid-template-columns: repeat(
      2,
      minmax(0, 1fr)
    );
  }

  .generated-at {
    text-align: left;
  }
}

@media (max-width: 960px) {
  .reports-main-grid,
  .reports-bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .reports-header {
    flex-direction: column;
  }

  .export-button {
    width: 100%;
    justify-content: center;
  }

  .filters-card,
  .statistics-grid {
    grid-template-columns: 1fr;
  }

  .bar-chart {
    grid-template-columns: repeat(
      12,
      minmax(35px, 1fr)
    );
    overflow-x: auto;
  }

  .bar-chart__column {
    min-width: 35px;
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

  .service-item {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .service-revenue {
    grid-column: 2;
    text-align: left;
  }
}
</style>