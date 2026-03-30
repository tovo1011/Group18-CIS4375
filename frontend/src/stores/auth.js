import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const token = ref(localStorage.getItem('authToken') || null)
  const error = ref(null)

  // Check if user was logged in before
  if (token.value) {
    isAuthenticated.value = true
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      user.value = JSON.parse(savedUser)
    }
    // Set default auth header
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  const login = async (email, password) => {
    try {
      error.value = null
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password
      })
      
      const { token: newToken, user: userData } = response.data
      
      user.value = userData
      isAuthenticated.value = true
      token.value = newToken
      
      localStorage.setItem('authToken', newToken)
      localStorage.setItem('user', JSON.stringify(userData))
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
      
      return userData
    } catch (err) {
      const message = err.response?.data?.message || 'Login failed. Please try again.'
      error.value = message
      throw new Error(message)
    }
  }

  const logout = () => {
    user.value = null
    isAuthenticated.value = false
    token.value = null
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
  }

  const getCurrentUser = async () => {
    try {
      if (!token.value) return null
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token.value}` }
      })
      user.value = response.data
      return response.data
    } catch (err) {
      logout()
      return null
    }
  }

  return {
    user,
    isAuthenticated,
    token,
    error,
    login,
    logout,
    getCurrentUser
  }
})
