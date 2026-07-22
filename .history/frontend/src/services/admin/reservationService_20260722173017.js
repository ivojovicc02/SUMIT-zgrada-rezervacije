import api from '../api'

export function getDashboard() {
  return api.get('/admin/dashboard')
}

const reservationService = {
  async getReservations(filters = {}) {
    const params = {}

    if (filters.status && filters.status !== 'all') {
      params.status = filters.status
    }

    if (filters.spaceId && filters.spaceId !== 'all') {
      params.space_id = filters.spaceId
    }

    if (filters.search?.trim()) {
      params.search = filters.search.trim()
    }

    if (filters.fromDate) {
      params.from_date = `${filters.fromDate}T00:00:00`
    }

    if (filters.toDate) {
      params.to_date = `${filters.toDate}T23:59:59`
    }

    const response = await api.get(
      '/admin/reservations',
      { params },
    )

    return response.data
  },
}

export default reservationService