import api from '../api'

export function getSpaces(params = {}) {
  return api.get('/admin/spaces', { params })
}

export function getSpaceById(spaceId) {
  return api.get(`/admin/spaces/${spaceId}`)
}