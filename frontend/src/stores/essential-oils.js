import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

export const useEssentialOilStore = defineStore('essential-oils', () => {
  const oils = ref([])
  const searchQuery = ref('')
  const filterSupplierId = ref('')
  const loading = ref(false)
  const error = ref(null)

  const filteredOils = computed(() => {
    return oils.value.filter(oil => {
      const matchesSearch = oil.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      const matchesSupplier = !filterSupplierId.value || oil.supplierId.toString() === filterSupplierId.value
      return matchesSearch && matchesSupplier
    })
  })

  const getOil = (id) => {
    return oils.value.find(o => o.id === id)
  }

  const fetchOils = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.get(`${API_URL}/essential-oils`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      oils.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch oils'
      console.error('Fetch oils error:', err)
    } finally {
      loading.value = false
    }
  }

  const addOil = async (oil) => {
    try {
      loading.value = true
      error.value = null
      
      // Check for duplicate oil name (case-insensitive)
      const isDuplicate = oils.value.some(o => 
        o.name.toLowerCase() === oil.name.toLowerCase()
      )
      if (isDuplicate) {
        error.value = `Oil "${oil.name}" already exists`
        throw new Error(error.value)
      }
      
      const response = await axios.post(`${API_URL}/essential-oils`, oil, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      oils.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message || 'Failed to add oil'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateOil = async (id, updates) => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.put(`${API_URL}/essential-oils/${id}`, updates, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      const index = oils.value.findIndex(o => o.id === id)
      if (index !== -1) {
        oils.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to update oil'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteOil = async (id) => {
    try {
      loading.value = true
      error.value = null
      await axios.delete(`${API_URL}/essential-oils/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      const index = oils.value.findIndex(o => o.id === id)
      if (index !== -1) {
        oils.value.splice(index, 1)
      }
      return true
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to delete oil'
      throw err
    } finally {
      loading.value = false
    }
  }

  const bulkDeleteOils = async (ids) => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.post(`${API_URL}/essential-oils/bulk-delete`, { ids }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      
      // Only remove from local state if backend confirms deletion was successful
      if (response.data.deletedCount > 0) {
        oils.value = oils.value.filter(o => !ids.includes(o.id))
      }
      
      // If not all deletions succeeded, log a warning
      if (response.data.deletedCount < response.data.requestedCount) {
        error.value = `Only ${response.data.deletedCount} of ${response.data.requestedCount} oils were deleted`
        console.warn('Bulk delete partial failure:', response.data)
        // Refetch to ensure UI is in sync with actual database state
        await fetchOils()
      }
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to bulk delete oils'
      // Refetch to ensure UI is in sync if there was an error
      try {
        await fetchOils()
      } catch (fetchErr) {
        console.error('Failed to refetch oils after delete error:', fetchErr)
      }
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
    oils,
    filteredOils,
    searchQuery,
    filterSupplierId,
    loading,
    error,
    getOil,
    fetchOils,
    addOil,
    updateOil,
    deleteOil,
    bulkDeleteOils,
    setSearchQuery,
    setFilterSupplier
  }
})
