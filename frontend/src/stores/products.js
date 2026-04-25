import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

function authHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem('authToken')}` }
}

export const useProductStore = defineStore('products', () => {
  const products = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchProducts = async () => {
    try {
      loading.value = true
      error.value = null
      const res = await axios.get(`${API_URL}/products`, { headers: authHeaders() })
      products.value = res.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch products'
    } finally {
      loading.value = false
    }
  }

  const addProduct = async (formData) => {
    try {
      loading.value = true
      error.value = null
      const res = await axios.post(`${API_URL}/products`, formData, {
        headers: { ...authHeaders(), 'Content-Type': 'multipart/form-data' }
      })
      products.value.push(res.data)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to add product'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateProduct = async (id, formData) => {
    try {
      loading.value = true
      error.value = null
      const res = await axios.put(`${API_URL}/products/${id}`, formData, {
        headers: { ...authHeaders(), 'Content-Type': 'multipart/form-data' }
      })
      const idx = products.value.findIndex(p => p.id === id)
      if (idx !== -1) products.value[idx] = res.data
      return res.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to update product'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteProduct = async (id) => {
    try {
      loading.value = true
      error.value = null
      await axios.delete(`${API_URL}/products/${id}`, { headers: authHeaders() })
      products.value = products.value.filter(p => p.id !== id)
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to delete product'
      throw err
    } finally {
      loading.value = false
    }
  }

  return { products, loading, error, fetchProducts, addProduct, updateProduct, deleteProduct }
})
