const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  'http://127.0.0.1:8000'

export const fallbackSpaceImage =
  'https://placehold.co/240x160?text=Nema+slike'

export function getSpaceImageUrl(url) {
  if (!url) {
    return fallbackSpaceImage
  }

  if (
    url.startsWith('http://') ||
    url.startsWith('https://')
  ) {
    return url
  }

  const normalizedUrl = url.startsWith('/')
    ? url
    : `/${url}`

  return `${API_BASE_URL}${normalizedUrl}`
}

export function getPrimarySpaceImage(space) {
  if (!Array.isArray(space?.images)) {
    return fallbackSpaceImage
  }

  const primaryImage = space.images.find(
    (image) => image.is_primary === true,
  )

  const imagePath =
    primaryImage?.url ||
    space.images[0]?.url

  return getSpaceImageUrl(imagePath)
}

export function formatSpaceType(spaceType) {
  const labels = {
    office_workspace: 'Uredi i radni prostori',
    conference: 'Konferencijske dvorane',
    outdoor: 'Vanjski prostori i park',
  }

  return (
    labels[spaceType] ||
    spaceType ||
    'Nije definirano'
  )
}

export function formatSpaceSubtype(spaceSubtype) {
  const labels = {
    private_office: 'Privatni ured',
    permanent_workspace: 'Stalno radno mjesto',
    flexible_package: 'Fleksibilni paket',
    virtual_office: 'Virtualni ured',
    meeting_room: 'Sala za sastanke',
    conference_hall: 'Konferencijska dvorana',
    terrace: 'Terasa',
    green_park: 'Zeleni park',
  }

  return (
    labels[spaceSubtype] ||
    spaceSubtype ||
    'Nije definirano'
  )
}

export function formatSpacePriceUnit(priceUnit) {
  const labels = {
    hour: 'po satu',
    day: 'po danu',
    month: 'mjesečno',
    reservation: 'po rezervaciji',
  }

  return labels[priceUnit] || priceUnit || ''
}

export function formatPrice(price) {
  const numericPrice = Number(price)

  if (Number.isNaN(numericPrice)) {
    return '0,00'
  }

  return new Intl.NumberFormat('hr-HR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numericPrice)
}