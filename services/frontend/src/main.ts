import './assets/main.css'
import './index.css'
import 'vue3-toastify/dist/index.css'
import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import axios from 'axios'
import messages from '@intlify/unplugin-vue-i18n/messages'

/** Initiate vue-i18n utility class */
const i18n = createI18n({
  locale: 'en_US',
  fallbackLocale: 'en_US',
  legacy: false,
  messages,
})

/** Create Vue app */
const app = createApp(App)

/** Set vue app to use i18n utility class instance */
app.use(i18n)

/** Set axios defaults */
axios.defaults.withCredentials = true
axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5051/' // the FastAPI backend

app.mount('#app')
