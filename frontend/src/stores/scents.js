import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

export const useScentStore = defineStore('scents', () => {
  const scents = ref([])
  const searchQuery = ref('')
  const filterNoteType = ref('')
  const loading = ref(false)
  const error = ref(null)

  const filteredScents = computed(() => {
    return scents.value.filter(scent => {
      if (scent.archivedAt) return false
      
      const matchesSearch = scent.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      
      let matchesFilter = true
      if (filterNoteType.value) {
        const noteType = filterNoteType.value
        matchesFilter = 
          scent.topNotes.toLowerCase().includes(noteType.toLowerCase()) ||
          scent.middleNotes.toLowerCase().includes(noteType.toLowerCase()) ||
          scent.baseNotes.toLowerCase().includes(noteType.toLowerCase())
      }
      
      return matchesSearch && matchesFilter
    })
  })

  const getScent = (id) => {
    return scents.value.find(s => s.id === id)
  }

  const fetchScents = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.get(`${API_URL}/scents`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      scents.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch scents'
      console.error('Fetch scents error:', err)
    } finally {
      loading.value = false
    }
  }

  const addScent = async (scent) => {
    try {
      loading.value = true
      error.value = null
      
      // Check for duplicate scent name (case-insensitive)
      const isDuplicate = scents.value.some(s => 
        s.name.toLowerCase() === scent.name.toLowerCase() && !s.archivedAt
      )
      if (isDuplicate) {
        error.value = `Scent "${scent.name}" already exists`
        throw new Error(error.value)
      }
      
      const response = await axios.post(`${API_URL}/scents`, scent, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      scents.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message || 'Failed to add scent'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateScent = async (id, updates) => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.put(`${API_URL}/scents/${id}`, updates, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      const index = scents.value.findIndex(s => s.id === id)
      if (index !== -1) {
        scents.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to update scent'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteScent = async (id) => {
    try {
      loading.value = true
      error.value = null
      await axios.delete(`${API_URL}/scents/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      const index = scents.value.findIndex(s => s.id === id)
      if (index !== -1) {
        scents.value.splice(index, 1)
      }
      return true
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to delete scent'
      throw err
    } finally {
      loading.value = false
    }
  }

  const setSearchQuery = (query) => {
    searchQuery.value = query
  }

  const setFilterNoteType = (noteType) => {
    filterNoteType.value = noteType
  }

  return {
    scents,
    filteredScents,
    searchQuery,
    filterNoteType,
    loading,
    error,
    getScent,
    fetchScents,
    addScent,
    updateScent,
    deleteScent,
    setSearchQuery,
    setFilterNoteType
  }
})
