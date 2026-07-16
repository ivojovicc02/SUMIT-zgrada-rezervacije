import api from '../api'

export function getSpaces(params = {}) {
  return api.get('/admin/spaces', { params })
}

export function createSpace(spaceData) {
  return api.post('/admin/spaces', spaceData)
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

export function uploadSpaceImages(
  spaceId,
  files,
  primaryIndex = 0,
) {
  if (!spaceId) {
    return Promise.reject(
      new Error('ID prostora nije proslijeđen.'),
    )
  }

  if (!files || files.length === 0) {
    return Promise.reject(
      new Error('Nije odabrana nijedna slika.'),
    )
  }

  const formData = new FormData()

  Array.from(files).forEach((file) => {
    formData.append('images', file)
  })

  return api.post(
    `/admin/spaces/${spaceId}/images`,
    formData,
    {
      params: {
        primary_index: primaryIndex,
      },
    },
  )
}
export function getSpaceCategories() {
  return api.get('/admin/space-categories')
}

export function getSpaceSubcategories(params = {}) {
  return api.get('/admin/space-subcategories', {
    params,
  })
}

export function createSpaceCategory(data) {
  return api.post('/admin/space-categories', data)
}

export function updateSpaceCategory(categoryId, data) {
  return api.put(
    `/admin/space-categories/${categoryId}`,
    data,
  )
}

export function deleteSpaceCategory(categoryId) {
  return api.delete(
    `/admin/space-categories/${categoryId}`,
  )
}

export function createSpaceSubcategory(data) {
  return api.post('/admin/space-subcategories', data)
}

export function updateSpaceSubcategory(
  subcategoryId,
  data,
) {
  return api.put(
    `/admin/space-subcategories/${subcategoryId}`,
    data,
  )
}

export function deleteSpaceSubcategory(
  subcategoryId,
) {
  return api.delete(
    `/admin/space-subcategories/${subcategoryId}`,
  )
}