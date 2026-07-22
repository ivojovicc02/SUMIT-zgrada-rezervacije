import {
  createRouter,
  createWebHistory,
} from 'vue-router'

import {
  initializeAuth,
  initialized,
  isAuthenticated,
} from '../services/admin/authService'

import PublicLayout from '../layouts/PublicLayout.vue'
import HomeView from '../views/public/HomeView.vue'
import SpacesView from '../views/public/SpacesView.vue'
import SpaceDetailsView from '../views/public/SpaceDetailsView.vue'
import ReservationView from '../views/public/ReservationView.vue'
import ReservationSuccessView from '../views/public/ReservationSuccessView.vue'
import AdminLoginView from '../views/admin/AdminLoginView.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import AdminDashboardView from '../views/admin/AdminDashboardView.vue'
import AdminSpacesView from '../views/admin/AdminSpacesView.vue'
import AdminReservationsView from '../views/admin/AdminReservationsView.vue'
import AdminReportsView from '../views/admin/AdminReportsView.vue'

const routes = [
  {
    path: '/',
    component: PublicLayout,
    children: [
      { path: '', name: 'home', component: HomeView },
      { path: 'prostori', name: 'public-spaces', component: SpacesView },
      { path: 'prostori/:id', name: 'public-space-details', component: SpaceDetailsView },
      { path: 'rezervacija', name: 'public-reservation', component: ReservationView },
      { path: 'rezervacija/potvrda', name: 'public-reservation-success', component: ReservationSuccessView },
    ],
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: AdminLoginView,
    meta: {
      guestOnly: true,
    },
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: AdminDashboardView,
      },
      {
        path: 'prostori',
        name: 'admin-spaces',
        component: AdminSpacesView,
      },
      {
        path: 'rezervacije',
        name: 'admin-reservations',
        component: AdminReservationsView,
      },
      {
        path: 'izvjestaji',
        name: 'admin-reports',
        component: AdminReportsView,
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  /*
   * Pri prvom pokretanju aplikacije ili osvježavanju stranice
   * provjerava se token preko backend rute /admin/me.
   */
  if (!initialized.value) {
    await initializeAuth()
  }

  /*
   * Prijavljeni administrator ne može ponovno otvoriti
   * stranicu za prijavu.
   */
  if (
    to.meta.guestOnly &&
    isAuthenticated.value
  ) {
    return {
      name: 'admin-dashboard',
    }
  }

  /*
   * Neprijavljeni korisnik ne može pristupiti admin rutama.
   * Čuva se ruta na koju je pokušao otići.
   */
  if (
    to.meta.requiresAuth &&
    !isAuthenticated.value
  ) {
    return {
      name: 'admin-login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  return true
})

export default router