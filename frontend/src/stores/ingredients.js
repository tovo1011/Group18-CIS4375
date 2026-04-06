import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

export const useIngredientStore = defineStore('ingredients', () => {
  const ingredients = ref([])
  const searchQuery = ref('')
  const filterSupplierId = ref('')
  const loading = ref(false)
  const error = ref(null)

  const filteredIngredients = computed(() => {
    return ingredients.value.filter(ing => {
      const matchesSearch = ing.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      const matchesSupplier = !filterSupplierId.value || ing.supplierId.toString() === filterSupplierId.value
      return matchesSearch && matchesSupplier
    })
  })

  const getIngredient = (id) => {
    return ingredients.value.find(i => i.id === id)
  }

  const fetchIngredients = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.get(`${API_URL}/ingredients`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      ingredients.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch ingredients'
      console.error('Fetch ingredients error:', err)
    } finally {
      loading.value = false
    }
  }

  const addIngredient = async (ingredient) => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.post(`${API_URL}/ingredients`, ingredient, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      ingredients.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to add ingredient'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateIngredient = async (id, updates) => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.put(`${API_URL}/ingredients/${id}`, updates, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      const index = ingredients.value.findIndex(i => i.id === id)
      if (index !== -1) {
        ingredients.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to update ingredient'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteIngredient = async (id) => {
    try {
      loading.value = true
      error.value = null
      await axios.delete(`${API_URL}/ingredients/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      const index = ingredients.value.findIndex(i => i.id === id)
      if (index !== -1) {
        ingredients.value.splice(index, 1)
      }
      return true
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to delete ingredient'
      throw err
    } finally {
      loading.value = false
    }
  }

  const setSearchQuery = (query) => {
    searchQuery.value = query
  }

  const setFilterSupplier = (supplierId) => {
    filterSupplierId.value = supplierId
  }

  return {
    ingredients,
    filteredIngredients,
    searchQuery,
    filterSupplierId,
    loading,
    error,
    getIngredient,
    fetchIngredients,
    addIngredient,
    updateIngredient,
    deleteIngredient,
    setSearchQuery,
    setFilterSupplier
  }
})
