import api from './api'

export function getAdmins() {
  return api.get('/admin/admins')
}

export function createAdmin(data) {
  return api.post('/admin/create-admin', data)
}

export function updateAdmin(adminId, data) {
  return api.patch(`/admin/admins/${adminId}`, data)
}