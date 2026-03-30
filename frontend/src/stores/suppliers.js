import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

export const useSupplierStore = defineStore('suppliers', () => {
  const suppliers = ref([])
  const loading = ref(false)
  const error = ref(null)

  const getSupplier = (id) => {
    return suppliers.value.find(s => s.id === id)
  }

  const fetchSuppliers = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.get(`${API_URL}/suppliers`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      suppliers.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch suppliers'
      console.error('Fetch suppliers error:', err)
    } finally {
      loading.value = false
    }
  }

  const addSupplier = async (supplier) => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.post(`${API_URL}/suppliers`, supplier, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      suppliers.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to add supplier'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateSupplier = async (id, updates) => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.put(`${API_URL}/suppliers/${id}`, updates, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      const index = suppliers.value.findIndex(s => s.id === id)
      if (index !== -1) {
        suppliers.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to update supplier'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteSupplier = async (id) => {
    try {
      loading.value = true
      error.value = null
      await axios.delete(`${API_URL}/suppliers/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      const index = suppliers.value.findIndex(s => s.id === id)
      if (index !== -1) {
        suppliers.value.splice(index, 1)
      }
      return true
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to delete supplier'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    suppliers,
    loading,
    error,
    getSupplier,
    fetchSuppliers,
    addSupplier,
    updateSupplier,
    deleteSupplier
  }
})
