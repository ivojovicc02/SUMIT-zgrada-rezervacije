import api from '../api'

export function getSpaces(params = {}) {
  return api.get('/admin/spaces', { params })
}

export function getSpaceById(spaceId) {
  if (!spaceId) {
    return Promise.reject(
      new Error('ID prostora nije proslijeđen.'),
    )
  }

  return api.get(`/admin/spaces/${spaceId}`)
}

export function deleteSpaceById(spaceId) {
  return api.delete(`/admin/spaces/${spaceId}`)
}