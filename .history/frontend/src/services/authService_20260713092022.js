import api from './api'

let currentUser = null
let initialized = false

export async function login(email, password) {
  const response = await api.post('/auth/login', {
    email,
    password,
  })

  currentUser = response.data.user ?? response.data

  return currentUser
}

export async function fetchCurrentUser() {
  try {
    const response = await api.get('/auth/me')
    currentUser = response.data.user ?? response.data
  } catch {
    currentUser = null
  } finally {
    initialized = true
  }

  return currentUser
}

export async function logout() {
  try {
    await api.post('/auth/logout')
  } finally {
    currentUser = null
    initialized = true
  }
}

export function getCurrentUser() {
  return currentUser
}

export function isInitialized() {
  return initialized
}

export function isAuthenticated() {
  return Boolean(currentUser)
}

export function isAdmin() {
  return currentUser?.role?.toUpperCase() === 'ADMIN'
}