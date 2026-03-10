import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const token = ref(localStorage.getItem('authToken') || null)

  // Check if user was logged in before
  if (token.value) {
    isAuthenticated.value = true
  }

  const login = (email, password) => {
    return new Promise((resolve, reject) => {
      // Simulate API call
      setTimeout(() => {
        if (email && password) {
          const userData = {
            id: 1,
            email: email,
            name: email.split('@')[0],
            role: 'manager'
          }
          user.value = userData
          isAuthenticated.value = true
          token.value = 'token_' + Date.now()
          localStorage.setItem('authToken', token.value)
          resolve(userData)
        } else {
          reject(new Error('Invalid credentials'))
        }
      }, 500)
    })
  }

  const logout = () => {
    user.value = null
    isAuthenticated.value = false
    token.value = null
    localStorage.removeItem('authToken')
  }

  return {
    user,
    isAuthenticated,
    token,
    login,
    logout
  }
})
