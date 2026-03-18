import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Configure axios with default base URL
// Change to your backend URL when deployed
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
axios.defaults.baseURL = API_BASE_URL

// Add request interceptor to include JWT token
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle 401 errors
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - redirect to login
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Make axios available globally
app.config.globalProperties.$axios = axios

app.use(createPinia())
app.use(router)
app.mount('#app')
