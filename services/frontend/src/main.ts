import './assets/main.css'
import './index.css'

import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'

const app = createApp(App)

axios.defaults.withCredentials = true
axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5051/'  // the FastAPI backend

app.mount('#app')
