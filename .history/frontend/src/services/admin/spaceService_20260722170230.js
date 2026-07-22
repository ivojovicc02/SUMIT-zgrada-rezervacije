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

export function updateSpaceById(spaceId, payload) {
  return api.put(
    `/admin/spaces/${spaceId}`,
    payload,
  )
}

export function uploadSpaceImages(
  spaceId,
  images,
  primaryIndex = null,
) {
  const formData = new FormData()

  for (const image of images) {
    formData.append('images', image)
  }

  const config = {}

  if (primaryIndex !== null) {
    config.params = {
      primary_index: primaryIndex,
    }
  }

  return api.post(
    `/admin/spaces/${spaceId}/images`,
    formData,
    config,
  )
}

export function deleteSpaceImage(
  spaceId,
  imageId,
) {
  return api.delete(
    `/admin/spaces/${spaceId}/images/${imageId}`,
  )
}

export function setPrimarySpaceImage(
  spaceId,
  imageId,
) {
  return api.patch(
    `/admin/spaces/${spaceId}/images/${imageId}/primary`,
  )
}

export default spaceService