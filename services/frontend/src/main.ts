import './assets/main.css'
import './index.css'

import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'
import { createI18n } from 'vue-i18n'
import messages from '@intlify/unplugin-vue-i18n/messages'

const i18n = createI18n({
  locale: 'en_US',
  fallbackLocale: 'en_US',
  legacy: false,
  messages
})

const app = createApp(App)

app.use(i18n)

axios.defaults.withCredentials = true
axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5051/'  // the FastAPI backend
axios.defaults.headers.common["ngrok-skip-browser-warning"] = '12345'

app.mount('#app')
