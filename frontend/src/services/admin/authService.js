import {
  computed,
  ref,
} from 'vue'

import api from '../api'

const TOKEN_KEY = 'admin_token'

export const authToken = ref(
  localStorage.getItem(TOKEN_KEY),
)

export const currentUser = ref(null)
export const initialized = ref(false)

export const isAuthenticated = computed(() => {
  return Boolean(
    authToken.value &&
    currentUser.value,
  )
})

function clearAuthState() {
  localStorage.removeItem(TOKEN_KEY)

  authToken.value = null
  currentUser.value = null
}

/**
 * Prijava administratora.
 */
export async function login(username, password) {
  const formData = new URLSearchParams()

  formData.append('username', username)
  formData.append('password', password)

  try {
    const response = await api.post(
      '/admin/login',
      formData,
      {
        headers: {
          'Content-Type':
            'application/x-www-form-urlencoded',
        },
      },
    )

    const token = response.data?.access_token

    if (!token) {
      throw new Error(
        'Backend nije vratio access token.',
      )
    }

    localStorage.setItem(TOKEN_KEY, token)
    authToken.value = token

    /*
     * Backend u login odgovoru već vraća user objekt.
     * Ako ga nema, dohvatit ćemo ga preko /admin/me.
     */
    if (response.data?.user) {
      currentUser.value = response.data.user
    } else {
      const userResponse = await api.get(
        '/admin/me',
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      currentUser.value = userResponse.data
    }

    initialized.value = true

    return currentUser.value
  } catch (error) {
    clearAuthState()
    initialized.value = true

    throw error
  }
}

/**
 * Poziva se pri prvom pokretanju aplikacije i nakon F5.
 * Postojeći token provjerava preko backenda.
 */
export async function initializeAuth() {
  const token = localStorage.getItem(TOKEN_KEY)

  if (!token) {
    clearAuthState()
    initialized.value = true

    return null
  }

  authToken.value = token

  try {
    const response = await api.get(
      '/admin/me',
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )

    currentUser.value = response.data

    return currentUser.value
  } catch (error) {
    /*
     * Token je istekao, neispravan je, korisnik je
     * deaktiviran ili više nema admin rolu.
     */
    clearAuthState()

    return null
  } finally {
    initialized.value = true
  }
}

/**
 * Odjava administratora.
 */
export function logout() {
  clearAuthState()
  initialized.value = true
}