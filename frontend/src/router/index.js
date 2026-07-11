import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/public/HomeView.vue'
import AdminLoginView from '../views/admin/AdminLoginView.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import AdminDashboardView from '../views/admin/AdminDashboardView.vue'
import AdminSpacesView from '../views/admin/AdminSpacesView.vue'
import AdminReservationsView from '../views/admin/AdminReservationsView.vue'
import AdminReportsView from '../views/admin/AdminReportsView.vue'

const routes = [
  // JAVNI DIO
  // Kolega kasnije ovdje može dodati svoje rute.
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

router.beforeEach((to) => {
  const isAdminLoggedIn = Boolean(
    localStorage.getItem('admin_token'),
  )

  if (to.meta.requiresAdmin && !isAdminLoggedIn) {
    return {
      name: 'admin-login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (to.meta.guestOnly && isAdminLoggedIn) {
    return {
      name: 'admin-dashboard',
    }
  }

  return true
})

export default router