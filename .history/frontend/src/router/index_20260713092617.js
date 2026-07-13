import {
  createRouter,
  createWebHistory,
} from 'vue-router'

import {
  fetchCurrentUser,
  initialized,
  isAdmin,
  isAuthenticated,
} from '../services/authService'

import HomeView from '../views/public/HomeView.vue'
import AdminLoginView from '../views/admin/AdminLoginView.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import AdminDashboardView from '../views/admin/AdminDashboardView.vue'
import AdminSpacesView from '../views/admin/AdminSpacesView.vue'
import AdminReservationsView from '../views/admin/AdminReservationsView.vue'
import AdminReportsView from '../views/admin/AdminReportsView.vue'

const routes = [
  // JAVNI DIO
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },

  // ADMIN LOGIN
  {
    path: '/admin/login',
    name: 'admin-login',
    component: AdminLoginView,
    meta: {
      guestOnly: true,
    },
  },

  // ADMIN DIO
  {
    path: '/admin',
    component: AdminLayout,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
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

  // Nepostojeća ruta vraća korisnika na početnu.
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
   * Nakon osvježavanja stranice frontend još ne zna
   * postoji li prijavljeni korisnik.
   *
   * Zato jednom poziva backend endpoint /auth/me.
   */
  if (!initialized.value) {
    await fetchCurrentUser()
  }

  /*
   * Ako je admin već prijavljen i pokuša otvoriti
   * login stranicu, preusmjeri ga na dashboard.
   */
  if (to.meta.guestOnly && isAdmin.value) {
    return {
      name: 'admin-dashboard',
    }
  }

  /*
   * Ako ruta zahtijeva prijavu, a korisnik nije
   * autentificiran, šaljemo ga na admin login.
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

  /*
   * Ako je korisnik prijavljen, ali nema ADMIN rolu,
   * ne dopuštamo pristup admin dijelu.
   */
  if (
    to.meta.requiresAdmin &&
    !isAdmin.value
  ) {
    return {
      name: 'admin-login',
    }
  }

  return true
})

export default router