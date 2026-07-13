<script setup>
import { ref } from 'vue'
import {
  useRoute,
  useRouter,
} from 'vue-router'
import { login } from '../../services/authService'

const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''
  loading.value = true

  try {
    await login(
      username.value,
      password.value,
    )

    const redirectPath =
      typeof route.query.redirect === 'string'
        ? route.query.redirect
        : '/admin'

    await router.replace(redirectPath)
  } catch (error) {
    if (error.response?.status === 401) {
      errorMessage.value =
        'Pogrešno korisničko ime ili lozinka.'
    } else if (error.response?.status === 422) {
      errorMessage.value =
        'Provjerite unesene podatke.'
    } else if (error.response?.data?.detail) {
      errorMessage.value =
        typeof error.response.data.detail === 'string'
          ? error.response.data.detail
          : 'Došlo je do pogreške pri prijavi.'
    } else if (error.code === 'ERR_NETWORK') {
      errorMessage.value =
        'Nije moguće povezati se s backendom.'
    } else {
      errorMessage.value =
        'Došlo je do pogreške prilikom prijave.'
    }

    console.error('Login greška:', error)
  } finally {
    loading.value = false
  }
}
</script>