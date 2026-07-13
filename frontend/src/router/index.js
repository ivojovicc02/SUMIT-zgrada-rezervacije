import {
  createRouter,
  createWebHistory,
} from 'vue-router'

import {
  initializeAuth,
  initialized,
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
  {
    path: '/',
    name: 'home',
    component: HomeView,
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
      requiresAuth: false,
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

router.beforeEach((to) => {
  if (!initialized.value) {
    initializeAuth()
  }

  if (
    to.meta.guestOnly &&
    isAuthenticated.value
  ) {
    return {
      name: 'admin-dashboard',
    }
  }

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