import { createApp } from 'vue'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import './styles/public/public.css'
import './style.css'

const app = createApp(App)

app.use(router)
app.use(vuetify)
app.mount('#app')