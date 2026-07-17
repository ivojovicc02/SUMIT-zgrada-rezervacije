<script setup>
import { watch, onUnmounted } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },

  space: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits([
  'close',
  'updated',
])

function closeModal() {
  emit('close')
}

function handleBackdropClick(event) {
  if (event.target === event.currentTarget) {
    closeModal()
  }
}

watch(
  () => props.isOpen,
  (isOpen) => {
    document.body.style.overflow = isOpen
      ? 'hidden'
      : ''
  },
)

onUnmounted(() => {
  document.body.style.overflow = ''
})

function submitForm() {
  console.log('Prostor za uređivanje:', props.space)

  // Kasnije:
  // await updateSpace(props.space.id, formData)
  // emit('updated')
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen && space"
      class="modal-backdrop"
      @click="handleBackdropClick"
    >
      <div
        class="space-edit-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-space-title"
      >
        <header class="modal-header">
          <div>
            <h2 id="edit-space-title">
              Uredi prostor
            </h2>

            <p>
              Uređujete prostor:
              <strong>{{ space.name }}</strong>
            </p>
          </div>

          <button
            type="button"
            class="modal-close-button"
            aria-label="Zatvori"
            @click="closeModal"
          >
            ×
          </button>
        </header>

        <form
          class="space-edit-form"
          @submit.prevent="submitForm"
        >
          <div class="form-group">
            <label for="edit-space-name">
              Naziv prostora
            </label>

            <input
              id="edit-space-name"
              type="text"
              :value="space.name"
              disabled
            />
          </div>

          <div class="form-group">
            <label for="edit-space-description">
              Opis
            </label>

            <textarea
              id="edit-space-description"
              :value="space.description"
              disabled
            ></textarea>
          </div>

          <p class="temporary-message">
            Modal je povezan. U sljedećem koraku dodat ćemo
            formu za uređivanje podataka i upravljanje slikama.
          </p>

          <footer class="modal-footer">
            <button
              type="button"
              class="secondary-button"
              @click="closeModal"
            >
              Odustani
            </button>

            <button
              type="submit"
              class="primary-button"
            >
              Spremi promjene
            </button>
          </footer>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgb(15 23 42 / 60%);
}

.space-edit-modal {
  width: min(760px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 16px;
  background: white;
  box-shadow: 0 24px 60px rgb(15 23 42 / 24%);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
}

.modal-header p {
  margin: 6px 0 0;
}

.modal-close-button {
  border: 0;
  background: transparent;
  font-size: 28px;
  cursor: pointer;
}

.space-edit-form {
  padding: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.form-group input,
.form-group textarea {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.temporary-message {
  padding: 16px;
  border-radius: 8px;
  background: #f3f4f6;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.secondary-button,
.primary-button {
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.secondary-button {
  border: 1px solid #d1d5db;
  background: white;
}

.primary-button {
  border: 0;
  background: #2563eb;
  color: white;
}
</style>