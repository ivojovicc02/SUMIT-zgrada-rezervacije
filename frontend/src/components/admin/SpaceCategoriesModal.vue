<script setup>
import {
  onMounted,
  ref,
  watch,
} from 'vue'

import {
  createSpaceCategory,
  createSpaceSubcategory,
  deleteSpaceCategory,
  deleteSpaceSubcategory,
  getSpaceCategories,
  getSpaceSubcategories,
  updateSpaceCategory,
  updateSpaceSubcategory,
} from '../../services/admin/spaceService'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits([
  'close',
  'changed',
])

const categories = ref([])
const subcategories = ref([])

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const newCategoryName = ref('')

const editingCategoryId = ref(null)
const editingCategoryName = ref('')

const addingSubcategoryCategoryId = ref(null)
const newSubcategoryName = ref('')

const editingSubcategoryId = ref(null)
const editingSubcategoryName = ref('')

const processingItem = ref(null)

function getErrorMessage(error, fallbackMessage) {
  const detail = error.response?.data?.detail

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    return (
      detail
        .map((item) => item.msg)
        .filter(Boolean)
        .join(', ') ||
      fallbackMessage
    )
  }

  return fallbackMessage
}

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function getSubcategoriesForCategory(categoryId) {
  return subcategories.value.filter(
    (subcategory) =>
      subcategory.category_id === categoryId,
  )
}

async function fetchCategoryData() {
  isLoading.value = true
  clearMessages()

  try {
    const [
      categoriesResponse,
      subcategoriesResponse,
    ] = await Promise.all([
      getSpaceCategories(),
      getSpaceSubcategories(),
    ])

    categories.value = Array.isArray(
      categoriesResponse.data,
    )
      ? categoriesResponse.data
      : []

    subcategories.value = Array.isArray(
      subcategoriesResponse.data,
    )
      ? subcategoriesResponse.data
      : []

    categories.value.sort((a, b) =>
      a.name.localeCompare(b.name, 'hr'),
    )

    subcategories.value.sort((a, b) =>
      a.name.localeCompare(b.name, 'hr'),
    )
  } catch (error) {
    console.error(
      'Greška pri dohvatu kategorija:',
      error,
    )

    errorMessage.value = getErrorMessage(
      error,
      'Nije moguće dohvatiti kategorije i podkategorije.',
    )
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (props.isOpen) {
    fetchCategoryData()
  }
})

watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      fetchCategoryData()
    } else {
      resetModalState()
    }
  },
)

function resetModalState() {
  clearMessages()

  newCategoryName.value = ''

  editingCategoryId.value = null
  editingCategoryName.value = ''

  addingSubcategoryCategoryId.value = null
  newSubcategoryName.value = ''

  editingSubcategoryId.value = null
  editingSubcategoryName.value = ''

  processingItem.value = null
}

function closeModal() {
  if (processingItem.value) {
    return
  }

  resetModalState()
  emit('close')
}

async function addCategory() {
  clearMessages()

  const name = newCategoryName.value.trim()

  if (!name) {
    errorMessage.value =
      'Unesite naziv kategorije.'

    return
  }

  processingItem.value = 'create-category'

  try {
    await createSpaceCategory({ name })

    newCategoryName.value = ''

    successMessage.value =
      'Kategorija je uspješno dodana.'

    await fetchCategoryData()
    emit('changed')
  } catch (error) {
    console.error(
      'Greška pri dodavanju kategorije:',
      error,
    )

    errorMessage.value = getErrorMessage(
      error,
      'Nije moguće dodati kategoriju.',
    )
  } finally {
    processingItem.value = null
  }
}

function startEditingCategory(category) {
  clearMessages()

  editingCategoryId.value = category.id
  editingCategoryName.value = category.name

  addingSubcategoryCategoryId.value = null
  editingSubcategoryId.value = null
}

function cancelEditingCategory() {
  editingCategoryId.value = null
  editingCategoryName.value = ''
}

async function saveCategory(categoryId) {
  clearMessages()

  const name =
    editingCategoryName.value.trim()

  if (!name) {
    errorMessage.value =
      'Naziv kategorije ne može biti prazan.'

    return
  }

  processingItem.value =
    `update-category-${categoryId}`

  try {
    await updateSpaceCategory(
      categoryId,
      { name },
    )

    cancelEditingCategory()

    successMessage.value =
      'Kategorija je uspješno uređena.'

    await fetchCategoryData()
    emit('changed')
  } catch (error) {
    console.error(
      'Greška pri uređivanju kategorije:',
      error,
    )

    errorMessage.value = getErrorMessage(
      error,
      'Nije moguće urediti kategoriju.',
    )
  } finally {
    processingItem.value = null
  }
}

async function removeCategory(category) {
  clearMessages()

  const confirmed = window.confirm(
    `Jeste li sigurni da želite obrisati kategoriju "${category.name}"?`,
  )

  if (!confirmed) {
    return
  }

  processingItem.value =
    `delete-category-${category.id}`

  try {
    await deleteSpaceCategory(category.id)

    successMessage.value =
      'Kategorija je uspješno obrisana.'

    await fetchCategoryData()
    emit('changed')
  } catch (error) {
    console.error(
      'Greška pri brisanju kategorije:',
      error,
    )

    errorMessage.value = getErrorMessage(
      error,
      'Nije moguće obrisati kategoriju.',
    )
  } finally {
    processingItem.value = null
  }
}

function startAddingSubcategory(categoryId) {
  clearMessages()

  addingSubcategoryCategoryId.value =
    categoryId

  newSubcategoryName.value = ''

  editingCategoryId.value = null
  editingSubcategoryId.value = null
}

function cancelAddingSubcategory() {
  addingSubcategoryCategoryId.value = null
  newSubcategoryName.value = ''
}

async function addSubcategory(categoryId) {
  clearMessages()

  const name =
    newSubcategoryName.value.trim()

  if (!name) {
    errorMessage.value =
      'Unesite naziv podkategorije.'

    return
  }

  processingItem.value =
    `create-subcategory-${categoryId}`

  try {
    await createSpaceSubcategory({
      name,
      category_id: categoryId,
    })

    cancelAddingSubcategory()

    successMessage.value =
      'Podkategorija je uspješno dodana.'

    await fetchCategoryData()
    emit('changed')
  } catch (error) {
    console.error(
      'Greška pri dodavanju podkategorije:',
      error,
    )

    errorMessage.value = getErrorMessage(
      error,
      'Nije moguće dodati podkategoriju.',
    )
  } finally {
    processingItem.value = null
  }
}

function startEditingSubcategory(
  subcategory,
) {
  clearMessages()

  editingSubcategoryId.value =
    subcategory.id

  editingSubcategoryName.value =
    subcategory.name

  editingCategoryId.value = null
  addingSubcategoryCategoryId.value = null
}

function cancelEditingSubcategory() {
  editingSubcategoryId.value = null
  editingSubcategoryName.value = ''
}

async function saveSubcategory(
  subcategory,
) {
  clearMessages()

  const name =
    editingSubcategoryName.value.trim()

  if (!name) {
    errorMessage.value =
      'Naziv podkategorije ne može biti prazan.'

    return
  }

  processingItem.value =
    `update-subcategory-${subcategory.id}`

  try {
    await updateSpaceSubcategory(
      subcategory.id,
      {
        name,
        category_id:
          subcategory.category_id,
      },
    )

    cancelEditingSubcategory()

    successMessage.value =
      'Podkategorija je uspješno uređena.'

    await fetchCategoryData()
    emit('changed')
  } catch (error) {
    console.error(
      'Greška pri uređivanju podkategorije:',
      error,
    )

    errorMessage.value = getErrorMessage(
      error,
      'Nije moguće urediti podkategoriju.',
    )
  } finally {
    processingItem.value = null
  }
}

async function removeSubcategory(
  subcategory,
) {
  clearMessages()

  const confirmed = window.confirm(
    `Jeste li sigurni da želite obrisati podkategoriju "${subcategory.name}"?`,
  )

  if (!confirmed) {
    return
  }

  processingItem.value =
    `delete-subcategory-${subcategory.id}`

  try {
    await deleteSpaceSubcategory(
      subcategory.id,
    )

    successMessage.value =
      'Podkategorija je uspješno obrisana.'

    await fetchCategoryData()
    emit('changed')
  } catch (error) {
    console.error(
      'Greška pri brisanju podkategorije:',
      error,
    )

    errorMessage.value = getErrorMessage(
      error,
      'Nije moguće obrisati podkategoriju.',
    )
  } finally {
    processingItem.value = null
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="modal-overlay"
      @click.self="closeModal"
    >
      <div
        class="categories-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="categories-modal-title"
      >
        <header class="modal-header">
          <div>
            <h2 id="categories-modal-title">
              Kategorije prostora
            </h2>

            <p>
              Dodajte, uredite ili obrišite
              kategorije i podkategorije.
            </p>
          </div>

          <button
            class="modal-close-button"
            type="button"
            aria-label="Zatvori"
            :disabled="Boolean(processingItem)"
            @click="closeModal"
          >
            ×
          </button>
        </header>

        <div class="categories-modal-content">
          <section class="new-category-section">
            <h3>Nova kategorija</h3>

            <div class="new-category-form">
              <input
                v-model="newCategoryName"
                type="text"
                maxlength="100"
                placeholder="Naziv kategorije"
                :disabled="Boolean(processingItem)"
                @keydown.enter.prevent="addCategory"
              />

              <button
                class="primary-button"
                type="button"
                :disabled="
                  Boolean(processingItem) ||
                  !newCategoryName.trim()
                "
                @click="addCategory"
              >
                {{
                  processingItem ===
                  'create-category'
                    ? 'Dodavanje...'
                    : 'Dodaj kategoriju'
                }}
              </button>
            </div>
          </section>

          <p
            v-if="errorMessage"
            class="categories-message categories-message--error"
          >
            {{ errorMessage }}
          </p>

          <p
            v-if="successMessage"
            class="categories-message categories-message--success"
          >
            {{ successMessage }}
          </p>

          <div
            v-if="isLoading"
            class="categories-state"
          >
            <div class="loading-spinner"></div>

            <p>
              Učitavanje kategorija...
            </p>
          </div>

          <div
            v-else-if="categories.length === 0"
            class="categories-state"
          >
            <h3>Nema kategorija</h3>

            <p>
              Dodajte prvu kategoriju prostora.
            </p>
          </div>

          <div
            v-else
            class="categories-list"
          >
            <article
              v-for="category in categories"
              :key="category.id"
              class="category-card"
            >
              <header class="category-card-header">
                <div
                  v-if="
                    editingCategoryId ===
                    category.id
                  "
                  class="inline-edit-form"
                >
                  <input
                    v-model="editingCategoryName"
                    type="text"
                    maxlength="100"
                    :disabled="
                      Boolean(processingItem)
                    "
                    @keydown.enter.prevent="
                      saveCategory(category.id)
                    "
                    @keydown.esc="
                      cancelEditingCategory
                    "
                  />

                  <button
                    class="small-button small-button--success"
                    type="button"
                    :disabled="
                      Boolean(processingItem)
                    "
                    @click="
                      saveCategory(category.id)
                    "
                  >
                    Spremi
                  </button>

                  <button
                    class="small-button"
                    type="button"
                    :disabled="
                      Boolean(processingItem)
                    "
                    @click="
                      cancelEditingCategory
                    "
                  >
                    Odustani
                  </button>
                </div>

                <template v-else>
                  <div>
                    <h3>
                      {{ category.name }}
                    </h3>

                    <span class="subcategory-count">
                      {{
                        getSubcategoriesForCategory(
                          category.id,
                        ).length
                      }}
                      podkategorija
                    </span>
                  </div>

                  <div class="category-actions">
                    <button
                      class="small-button"
                      type="button"
                      title="Uredi kategoriju"
                      :disabled="
                        Boolean(processingItem)
                      "
                      @click="
                        startEditingCategory(
                          category,
                        )
                      "
                    >
                      Uredi
                    </button>

                    <button
                      class="small-button small-button--danger"
                      type="button"
                      title="Obriši kategoriju"
                      :disabled="
                        Boolean(processingItem)
                      "
                      @click="
                        removeCategory(category)
                      "
                    >
                      Obriši
                    </button>
                  </div>
                </template>
              </header>

              <div class="subcategories-section">
                <div
                  v-if="
                    getSubcategoriesForCategory(
                      category.id,
                    ).length
                  "
                  class="subcategories-list"
                >
                  <div
                    v-for="subcategory in getSubcategoriesForCategory(
                      category.id,
                    )"
                    :key="subcategory.id"
                    class="subcategory-item"
                  >
                    <div
                      v-if="
                        editingSubcategoryId ===
                        subcategory.id
                      "
                      class="inline-edit-form"
                    >
                      <input
                        v-model="
                          editingSubcategoryName
                        "
                        type="text"
                        maxlength="100"
                        :disabled="
                          Boolean(processingItem)
                        "
                        @keydown.enter.prevent="
                          saveSubcategory(
                            subcategory,
                          )
                        "
                        @keydown.esc="
                          cancelEditingSubcategory
                        "
                      />

                      <button
                        class="small-button small-button--success"
                        type="button"
                        :disabled="
                          Boolean(processingItem)
                        "
                        @click="
                          saveSubcategory(
                            subcategory,
                          )
                        "
                      >
                        Spremi
                      </button>

                      <button
                        class="small-button"
                        type="button"
                        :disabled="
                          Boolean(processingItem)
                        "
                        @click="
                          cancelEditingSubcategory
                        "
                      >
                        Odustani
                      </button>
                    </div>

                    <template v-else>
                      <span>
                        {{ subcategory.name }}
                      </span>

                      <div class="subcategory-actions">
                        <button
                          class="icon-text-button"
                          type="button"
                          :disabled="
                            Boolean(processingItem)
                          "
                          @click="
                            startEditingSubcategory(
                              subcategory,
                            )
                          "
                        >
                          Uredi
                        </button>

                        <button
                          class="icon-text-button icon-text-button--danger"
                          type="button"
                          :disabled="
                            Boolean(processingItem)
                          "
                          @click="
                            removeSubcategory(
                              subcategory,
                            )
                          "
                        >
                          Obriši
                        </button>
                      </div>
                    </template>
                  </div>
                </div>

                <p
                  v-else
                  class="no-subcategories"
                >
                  Ova kategorija nema
                  podkategorija.
                </p>

                <div
                  v-if="
                    addingSubcategoryCategoryId ===
                    category.id
                  "
                  class="new-subcategory-form"
                >
                  <input
                    v-model="
                      newSubcategoryName
                    "
                    type="text"
                    maxlength="100"
                    placeholder="Naziv podkategorije"
                    :disabled="
                      Boolean(processingItem)
                    "
                    @keydown.enter.prevent="
                      addSubcategory(
                        category.id,
                      )
                    "
                    @keydown.esc="
                      cancelAddingSubcategory
                    "
                  />

                  <button
                    class="small-button small-button--success"
                    type="button"
                    :disabled="
                      Boolean(processingItem) ||
                      !newSubcategoryName.trim()
                    "
                    @click="
                      addSubcategory(
                        category.id,
                      )
                    "
                  >
                    Dodaj
                  </button>

                  <button
                    class="small-button"
                    type="button"
                    :disabled="
                      Boolean(processingItem)
                    "
                    @click="
                      cancelAddingSubcategory
                    "
                  >
                    Odustani
                  </button>
                </div>

                <button
                  v-else
                  class="add-subcategory-button"
                  type="button"
                  :disabled="
                    Boolean(processingItem)
                  "
                  @click="
                    startAddingSubcategory(
                      category.id,
                    )
                  "
                >
                  + Dodaj podkategoriju
                </button>
              </div>
            </article>
          </div>
        </div>

        <footer class="categories-modal-footer">
          <button
            class="secondary-button"
            type="button"
            :disabled="Boolean(processingItem)"
            @click="closeModal"
          >
            Zatvori
          </button>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.categories-modal {
  width: min(850px, calc(100vw - 32px));
  max-height: calc(100vh - 48px);
  overflow: hidden;
  border-radius: 16px;
  background: #ffffff;
  box-shadow:
    0 24px 60px rgba(15, 23, 42, 0.25);
}

.categories-modal-content {
  max-height: calc(100vh - 220px);
  overflow-y: auto;
  padding: 22px;
}

.new-category-section {
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
}

.new-category-section h3 {
  margin: 0 0 12px;
}

.new-category-form {
  display: flex;
  gap: 12px;
}

.new-category-form input {
  flex: 1;
}

.categories-message {
  margin: 16px 0 0;
  padding: 11px 14px;
  border-radius: 8px;
  font-size: 14px;
}

.categories-message--error {
  border: 1px solid #fecaca;
  color: #b91c1c;
  background: #fef2f2;
}

.categories-message--success {
  border: 1px solid #bbf7d0;
  color: #15803d;
  background: #f0fdf4;
}

.categories-state {
  padding: 40px 20px;
  text-align: center;
  color: #64748b;
}

.categories-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 18px;
}

.category-card {
  overflow: hidden;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #ffffff;
}

.category-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  background: #f8fafc;
}

.category-card-header h3 {
  margin: 0;
  color: #0f172a;
  font-size: 17px;
}

.subcategory-count {
  display: block;
  margin-top: 4px;
  color: #64748b;
  font-size: 13px;
}

.category-actions,
.subcategory-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.subcategories-section {
  padding: 14px 18px 18px;
}

.subcategories-list {
  display: flex;
  flex-direction: column;
}

.subcategory-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 11px 4px;
  border-bottom: 1px solid #f1f5f9;
}

.subcategory-item:last-child {
  border-bottom: none;
}

.subcategory-item > span {
  color: #334155;
}

.no-subcategories {
  margin: 4px 0 14px;
  color: #94a3b8;
  font-size: 14px;
}

.inline-edit-form,
.new-subcategory-form {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 8px;
}

.inline-edit-form input,
.new-subcategory-form input {
  flex: 1;
  min-width: 0;
}

.new-subcategory-form {
  margin-top: 14px;
}

.small-button,
.icon-text-button,
.add-subcategory-button {
  border: none;
  background: transparent;
  cursor: pointer;
}

.small-button {
  padding: 7px 11px;
  border: 1px solid #cbd5e1;
  border-radius: 7px;
  color: #334155;
  background: #ffffff;
  font-size: 13px;
}

.small-button--success {
  border-color: #86efac;
  color: #15803d;
  background: #f0fdf4;
}

.small-button--danger {
  border-color: #fecaca;
  color: #dc2626;
  background: #fef2f2;
}

.icon-text-button {
  padding: 4px;
  color: #475569;
  font-size: 13px;
}

.icon-text-button--danger {
  color: #dc2626;
}

.add-subcategory-button {
  margin-top: 14px;
  padding: 0;
  color: #2563eb;
  font-weight: 600;
}

.small-button:disabled,
.icon-text-button:disabled,
.add-subcategory-button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.categories-modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 15px 22px;
  border-top: 1px solid #e2e8f0;
  background: #ffffff;
}

@media (max-width: 650px) {
  .new-category-form,
  .category-card-header,
  .inline-edit-form,
  .new-subcategory-form {
    align-items: stretch;
    flex-direction: column;
  }

  .category-actions {
    align-self: flex-start;
  }

  .subcategory-item {
    align-items: flex-start;
  }
}
</style>