import './assets/main.css'
import './index.css'

import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'
import router from './router'

const app = createApp(App)

axios.defaults.withCredentials = true
axios.defaults.baseURL = 'http://localhost:5050/'  // the FastAPI backend

app.use(router)

app.mount('#app')