<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const statistics = ref({
  totalReservations: 148,
  todayReservations: 6,
  activeSpaces: 12,
  monthlyRevenue: 8420,
})

const todayReservations = ref([
  {
    id: 1,
    eventName: 'Radionica umjetne inteligencije',
    customerName: 'SUMIT',
    spaceName: 'Konferencijska dvorana A',
    startTime: '09:00',
    endTime: '12:00',
    guests: 85,
    status: 'confirmed',
  },
  {
    id: 2,
    eventName: 'Sastanak projektnog tima',
    customerName: 'Ivan Marić',
    spaceName: 'Ured 204',
    startTime: '10:30',
    endTime: '11:30',
    guests: 8,
    status: 'confirmed',
  },
  {
    id: 3,
    eventName: 'Prezentacija studentskih projekata',
    customerName: 'FSRE',
    spaceName: 'Multimedijalna dvorana',
    startTime: '13:00',
    endTime: '15:30',
    guests: 55,
    status: 'confirmed',
  },
  {
    id: 4,
    eventName: 'Poslovni sastanak',
    customerName: 'Digital Solutions d.o.o.',
    spaceName: 'Ured 102',
    startTime: '16:00',
    endTime: '17:00',
    guests: 5,
    status: 'confirmed',
  },
])

const recentReservations = ref([
  {
    id: 101,
    eventName: 'Seminar digitalnog marketinga',
    customerName: 'Ana Kovač',
    spaceName: 'Konferencijska dvorana B',
    date: '18. 7. 2026.',
    time: '09:00 – 13:00',
    status: 'confirmed',
  },
  {
    id: 102,
    eventName: 'IT meetup Mostar',
    customerName: 'Mostar Tech Community',
    spaceName: 'Vanjski prostor',
    date: '19. 7. 2026.',
    time: '18:00 – 22:00',
    status: 'confirmed',
  },
  {
    id: 103,
    eventName: 'Intervju za posao',
    customerName: 'TechVision d.o.o.',
    spaceName: 'Ured 205',
    date: '20. 7. 2026.',
    time: '11:00 – 12:00',
    status: 'confirmed',
  },
  {
    id: 104,
    eventName: 'Edukacija zaposlenika',
    customerName: 'Algebra Mostar',
    spaceName: 'Multimedijalna dvorana',
    date: '21. 7. 2026.',
    time: '10:00 – 15:00',
    status: 'cancelled',
  },
  {
    id: 105,
    eventName: 'Sastanak uprave',
    customerName: 'Sveučilište u Mostaru',
    spaceName: 'Konferencijska dvorana A',
    date: '22. 7. 2026.',
    time: '09:30 – 11:00',
    status: 'confirmed',
  },
])

const spaceOccupancy = ref([
  {
    id: 1,
    name: 'Konferencijska dvorana A',
    status: 'occupied',
    currentEvent: 'Radionica umjetne inteligencije',
    occupiedUntil: '12:00',
  },
  {
    id: 2,
    name: 'Ured 204',
    status: 'occupied',
    currentEvent: 'Sastanak projektnog tima',
    occupiedUntil: '11:30',
  },
  {
    id: 3,
    name: 'Multimedijalna dvorana',
    status: 'available',
    currentEvent: null,
    occupiedUntil: null,
  },
  {
    id: 4,
    name: 'Konferencijska dvorana B',
    status: 'available',
    currentEvent: null,
    occupiedUntil: null,
  },
  {
    id: 5,
    name: 'Vanjski prostor',
    status: 'available',
    currentEvent: null,
    occupiedUntil: null,
  },
])

const currentDate = computed(() => {
  return new Intl.DateTimeFormat('hr-HR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date())
})

const occupiedSpacesCount = computed(() => {
  return spaceOccupancy.value.filter(
    (space) => space.status === 'occupied',
  ).length
})

const availableSpacesCount = computed(() => {
  return spaceOccupancy.value.filter(
    (space) => space.status === 'available',
  ).length
})

function formatCurrency(value) {
  return new Intl.NumberFormat('hr-HR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)
}

function getStatusLabel(status) {
  const labels = {
    confirmed: 'Potvrđena',
    cancelled: 'Otkazana',
    completed: 'Završena',
  }

  return labels[status] || status
}

function goToSpaces() {
  router.push({
    name: 'admin-spaces',
  })
}

function goToReservations() {
  router.push({
    name: 'admin-reservations',
  })
}

function goToReports() {
  router.push({
    name: 'admin-reports',
  })
}
</script>

<template>
  <section class="dashboard-page">
    <header class="dashboard-header">
      <div>
        <p class="dashboard-eyebrow">
          Administracija
        </p>

        <h1>Pregled sustava</h1>

        <p class="dashboard-date">
          {{ currentDate }}
        </p>
      </div>

      <button
        type="button"
        class="header-action"
        @click="goToReservations"
      >
        Pregled rezervacija
      </button>
    </header>

    <div class="stats-grid">
      <article class="stat-card">
        <div class="stat-card__top">
          <span class="stat-icon">
            📅
          </span>

          <span class="stat-badge stat-badge--positive">
            +12 ovaj mjesec
          </span>
        </div>

        <span class="stat-label">
          Ukupno rezervacija
        </span>

        <strong>
          {{ statistics.totalReservations }}
        </strong>

        <p>
          Sve rezervacije u sustavu
        </p>
      </article>

      <article class="stat-card">
        <div class="stat-card__top">
          <span class="stat-icon">
            🕒
          </span>

          <span class="stat-badge">
            Danas
          </span>
        </div>

        <span class="stat-label">
          Današnje rezervacije
        </span>

        <strong>
          {{ statistics.todayReservations }}
        </strong>

        <p>
          {{ occupiedSpacesCount }} prostora trenutno zauzeto
        </p>
      </article>

      <article class="stat-card">
        <div class="stat-card__top">
          <span class="stat-icon">
            🏢
          </span>

          <span class="stat-badge stat-badge--positive">
            Aktivno
          </span>
        </div>

        <span class="stat-label">
          Aktivni prostori
        </span>

        <strong>
          {{ statistics.activeSpaces }}
        </strong>

        <p>
          {{ availableSpacesCount }} trenutno dostupno
        </p>
      </article>

      <article class="stat-card">
        <div class="stat-card__top">
          <span class="stat-icon">
            💰
          </span>

          <span class="stat-badge stat-badge--positive">
            Ovaj mjesec
          </span>
        </div>

        <span class="stat-label">
          Mjesečni prihod
        </span>

        <strong>
          {{ formatCurrency(statistics.monthlyRevenue) }}
          KM
        </strong>

        <p>
          Ukupno naplaćene rezervacije
        </p>
      </article>
    </div>

    <div class="dashboard-grid">
      <article class="dashboard-card today-card">
        <div class="card-header">
          <div>
            <h2>Današnji raspored</h2>

            <p>
              Rezervacije koje se održavaju danas
            </p>
          </div>

          <span class="count-badge">
            {{ todayReservations.length }}
          </span>
        </div>

        <div
          v-if="todayReservations.length"
          class="schedule-list"
        >
          <div
            v-for="reservation in todayReservations"
            :key="reservation.id"
            class="schedule-item"
          >
            <div class="schedule-time">
              <strong>
                {{ reservation.startTime }}
              </strong>

              <span>
                {{ reservation.endTime }}
              </span>
            </div>

            <div class="schedule-line">
              <span></span>
            </div>

            <div class="schedule-content">
              <div class="schedule-content__top">
                <div>
                  <h3>
                    {{ reservation.eventName }}
                  </h3>

                  <p>
                    {{ reservation.customerName }}
                  </p>
                </div>

                <span class="status-badge status-badge--confirmed">
                  Potvrđena
                </span>
              </div>

              <div class="schedule-details">
                <span>
                  🏢 {{ reservation.spaceName }}
                </span>

                <span>
                  👥 {{ reservation.guests }} gostiju
                </span>
              </div>
            </div>
          </div>
        </div>

        <div
          v-else
          class="empty-state"
        >
          <span>📭</span>

          <p>Danas nema rezervacija.</p>
        </div>
      </article>

      <aside class="dashboard-card quick-actions-card">
        <div class="card-header">
          <div>
            <h2>Brze akcije</h2>

            <p>
              Najčešće administrativne radnje
            </p>
          </div>
        </div>

        <div class="quick-actions">
          <button
            type="button"
            class="quick-action"
            @click="goToReservations"
          >
            <span class="quick-action__icon">
              📅
            </span>

            <span>
              <strong>
                Pregled rezervacija
              </strong>

              <small>
                Upravljaj svim rezervacijama
              </small>
            </span>

            <span class="quick-action__arrow">
              →
            </span>
          </button>

          <button
            type="button"
            class="quick-action"
            @click="goToSpaces"
          >
            <span class="quick-action__icon">
              🏢
            </span>

            <span>
              <strong>
                Upravljanje prostorima
              </strong>

              <small>
                Dodaj ili uredi prostor
              </small>
            </span>

            <span class="quick-action__arrow">
              →
            </span>
          </button>

          <button
            type="button"
            class="quick-action"
            @click="goToReports"
          >
            <span class="quick-action__icon">
              📊
            </span>

            <span>
              <strong>
                Otvori izvještaje
              </strong>

              <small>
                Analiziraj prihode i korištenje
              </small>
            </span>

            <span class="quick-action__arrow">
              →
            </span>
          </button>
        </div>

        <div class="occupancy-summary">
          <div class="occupancy-summary__header">
            <span>Trenutna zauzetost</span>

            <strong>
              {{ occupiedSpacesCount }}/
              {{ spaceOccupancy.length }}
            </strong>
          </div>

          <div class="progress-bar">
            <div
              class="progress-bar__value"
              :style="{
                width: `${
                  (
                    occupiedSpacesCount /
                    spaceOccupancy.length
                  ) * 100
                }%`,
              }"
            ></div>
          </div>

          <p>
            {{ occupiedSpacesCount }} zauzeto,
            {{ availableSpacesCount }} dostupno
          </p>
        </div>
      </aside>
    </div>

    <div class="dashboard-bottom-grid">
      <article class="dashboard-card">
        <div class="card-header">
          <div>
            <h2>Posljednje rezervacije</h2>

            <p>
              Nedavno zaprimljeni zahtjevi
            </p>
          </div>

          <button
            type="button"
            class="text-button"
            @click="goToReservations"
          >
            Prikaži sve
          </button>
        </div>

        <div class="table-wrapper">
          <table class="reservations-table">
            <thead>
              <tr>
                <th>Događaj</th>
                <th>Prostor</th>
                <th>Termin</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="reservation in recentReservations"
                :key="reservation.id"
              >
                <td>
                  <strong>
                    {{ reservation.eventName }}
                  </strong>

                  <span>
                    {{ reservation.customerName }}
                  </span>
                </td>

                <td>
                  {{ reservation.spaceName }}
                </td>

                <td>
                  <strong>
                    {{ reservation.date }}
                  </strong>

                  <span>
                    {{ reservation.time }}
                  </span>
                </td>

                <td>
                  <span
                    class="status-badge"
                    :class="{
                      'status-badge--confirmed':
                        reservation.status ===
                        'confirmed',

                      'status-badge--cancelled':
                        reservation.status ===
                        'cancelled',
                    }"
                  >
                    {{
                      getStatusLabel(
                        reservation.status,
                      )
                    }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="dashboard-card">
        <div class="card-header">
          <div>
            <h2>Status prostora</h2>

            <p>
              Trenutna dostupnost prostora
            </p>
          </div>

          <button
            type="button"
            class="text-button"
            @click="goToSpaces"
          >
            Upravljaj
          </button>
        </div>

        <div class="spaces-list">
          <div
            v-for="space in spaceOccupancy"
            :key="space.id"
            class="space-status-item"
          >
            <span
              class="space-status-dot"
              :class="{
                'space-status-dot--occupied':
                  space.status === 'occupied',

                'space-status-dot--available':
                  space.status === 'available',
              }"
            ></span>

            <div class="space-status-content">
              <strong>
                {{ space.name }}
              </strong>

              <span v-if="space.status === 'occupied'">
                {{ space.currentEvent }}
              </span>

              <span v-else>
                Trenutno dostupan
              </span>
            </div>

            <div class="space-status-meta">
              <span
                class="status-badge"
                :class="{
                  'status-badge--occupied':
                    space.status === 'occupied',

                  'status-badge--available':
                    space.status === 'available',
                }"
              >
                {{
                  space.status === 'occupied'
                    ? 'Zauzet'
                    : 'Dostupan'
                }}
              </span>

              <small v-if="space.occupiedUntil">
                do {{ space.occupiedUntil }}
              </small>
            </div>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.dashboard-eyebrow {
  margin: 0 0 6px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dashboard-header h1 {
  margin: 0;
  color: #0f172a;
  font-size: clamp(26px, 3vw, 36px);
}

.dashboard-date {
  margin: 8px 0 0;
  color: #64748b;
  text-transform: capitalize;
}

.header-action {
  padding: 11px 16px;
  border: 0;
  border-radius: 10px;
  background: #2563eb;
  color: white;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  transition:
    background 0.2s ease,
    transform 0.2s ease;
}

.header-action:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card,
.dashboard-card {
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
  box-shadow: 0 14px 32px rgb(15 23 42 / 9%);
}

.stat-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
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
.count-badge {
  padding: 5px 9px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

.stat-badge--positive {
  background: #ecfdf5;
  color: #047857;
}

.stat-label {
  color: #64748b;
  font-size: 14px;
  font-weight: 600;
}

.stat-card strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 30px;
  line-height: 1.2;
}

.stat-card p {
  margin: 8px 0 0;
  color: #94a3b8;
  font-size: 13px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(280px, 0.8fr);
  gap: 20px;
}

.dashboard-bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(320px, 0.8fr);
  gap: 20px;
}

.dashboard-card {
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

.count-badge {
  min-width: 30px;
  text-align: center;
}

.schedule-list {
  display: flex;
  flex-direction: column;
}

.schedule-item {
  display: grid;
  grid-template-columns: 58px 18px minmax(0, 1fr);
  min-height: 104px;
}

.schedule-time {
  display: flex;
  flex-direction: column;
  padding-top: 3px;
}

.schedule-time strong {
  color: #0f172a;
  font-size: 14px;
}

.schedule-time span {
  margin-top: 3px;
  color: #94a3b8;
  font-size: 12px;
}

.schedule-line {
  position: relative;
  display: flex;
  justify-content: center;
}

.schedule-line::before {
  position: absolute;
  top: 12px;
  bottom: -12px;
  width: 2px;
  background: #e2e8f0;
  content: '';
}

.schedule-item:last-child .schedule-line::before {
  bottom: 70px;
}

.schedule-line span {
  position: relative;
  z-index: 1;
  width: 10px;
  height: 10px;
  margin-top: 5px;
  border: 3px solid white;
  border-radius: 50%;
  background: #2563eb;
  box-shadow: 0 0 0 2px #bfdbfe;
}

.schedule-content {
  padding: 0 0 22px 12px;
}

.schedule-content__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.schedule-content h3 {
  margin: 0;
  color: #0f172a;
  font-size: 15px;
}

.schedule-content p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

.schedule-details {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 12px;
  color: #64748b;
  font-size: 12px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  width: max-content;
  padding: 5px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}

.status-badge--confirmed,
.status-badge--available {
  background: #ecfdf5;
  color: #047857;
}

.status-badge--cancelled {
  background: #fff1f2;
  color: #be123c;
}

.status-badge--occupied {
  background: #fff7ed;
  color: #c2410c;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quick-action {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 13px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
  color: inherit;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    transform 0.2s ease;
}

.quick-action:hover {
  border-color: #bfdbfe;
  background: #eff6ff;
  transform: translateX(2px);
}

.quick-action__icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 10px;
  background: white;
  font-size: 19px;
}

.quick-action strong,
.quick-action small {
  display: block;
}

.quick-action strong {
  color: #0f172a;
  font-size: 13px;
}

.quick-action small {
  margin-top: 3px;
  color: #94a3b8;
}

.quick-action__arrow {
  color: #2563eb;
  font-size: 20px;
}

.occupancy-summary {
  margin-top: 22px;
  padding: 16px;
  border-radius: 12px;
  background: #f8fafc;
}

.occupancy-summary__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #475569;
  font-size: 13px;
}

.occupancy-summary__header strong {
  color: #0f172a;
}

.progress-bar {
  height: 8px;
  margin-top: 12px;
  overflow: hidden;
  border-radius: 999px;
  background: #e2e8f0;
}

.progress-bar__value {
  height: 100%;
  border-radius: inherit;
  background: #2563eb;
}

.occupancy-summary p {
  margin: 9px 0 0;
  color: #94a3b8;
  font-size: 12px;
}

.text-button {
  padding: 0;
  border: 0;
  background: transparent;
  color: #2563eb;
  font: inherit;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.table-wrapper {
  overflow-x: auto;
}

.reservations-table {
  width: 100%;
  border-collapse: collapse;
}

.reservations-table th {
  padding: 0 12px 11px;
  border-bottom: 1px solid #e2e8f0;
  color: #94a3b8;
  font-size: 11px;
  font-weight: 700;
  text-align: left;
  text-transform: uppercase;
}

.reservations-table td {
  padding: 14px 12px;
  border-bottom: 1px solid #f1f5f9;
  color: #475569;
  font-size: 13px;
}

.reservations-table tbody tr:last-child td {
  border-bottom: 0;
}

.reservations-table td strong,
.reservations-table td span {
  display: block;
}

.reservations-table td strong {
  color: #0f172a;
  font-size: 13px;
}

.reservations-table td span:not(.status-badge) {
  margin-top: 4px;
  color: #94a3b8;
  font-size: 12px;
}

.spaces-list {
  display: flex;
  flex-direction: column;
}

.space-status-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 13px 0;
  border-bottom: 1px solid #f1f5f9;
}

.space-status-item:last-child {
  border-bottom: 0;
}

.space-status-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.space-status-dot--occupied {
  background: #f97316;
  box-shadow: 0 0 0 4px #ffedd5;
}

.space-status-dot--available {
  background: #10b981;
  box-shadow: 0 0 0 4px #d1fae5;
}

.space-status-content strong,
.space-status-content span {
  display: block;
}

.space-status-content strong {
  color: #0f172a;
  font-size: 13px;
}

.space-status-content span {
  margin-top: 4px;
  overflow: hidden;
  color: #94a3b8;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.space-status-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.space-status-meta small {
  color: #94a3b8;
}

.empty-state {
  display: grid;
  min-height: 220px;
  place-items: center;
  align-content: center;
  color: #94a3b8;
  text-align: center;
}

.empty-state span {
  font-size: 36px;
}

.empty-state p {
  margin: 10px 0 0;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 620px) {
  .dashboard-header {
    flex-direction: column;
  }

  .header-action {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-card {
    padding: 17px;
  }

  .schedule-content__top {
    flex-direction: column;
  }

  .reservations-table th:nth-child(2),
  .reservations-table td:nth-child(2) {
    display: none;
  }

  .space-status-item {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .space-status-meta {
    grid-column: 2;
    align-items: flex-start;
  }
}
</style>