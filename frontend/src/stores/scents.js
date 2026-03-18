import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useScentStore = defineStore('scents', () => {
  const scents = ref([
    {
      id: 1,
      name: 'Rose Elegance',
      topNotes: 'Bergamot, Lemon',
      middleNotes: 'Rose, Jasmine',
      baseNotes: 'Sandalwood, Musk',
      createdBy: 'admin@t4scents.com',
      createdAt: '2025-01-15',
      archivedAt: null
    },
    {
      id: 2,
      name: 'Ocean Breeze',
      topNotes: 'Sea Salt, Grapefruit',
      middleNotes: 'Aquatic Notes, Jasmine',
      baseNotes: 'Cedarwood, Amber',
      createdBy: 'admin@t4scents.com',
      createdAt: '2025-02-03',
      archivedAt: null
    }
  ])

  const searchQuery = ref('')
  const filterNoteType = ref('')

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

  const addScent = (scent) => {
    const newScent = {
      id: Math.max(...scents.value.map(s => s.id), 0) + 1,
      ...scent,
      createdAt: new Date().toISOString().split('T')[0],
      archivedAt: null
    }
    scents.value.push(newScent)
    return newScent
  }

  const updateScent = (id, updates) => {
    const index = scents.value.findIndex(s => s.id === id)
    if (index !== -1) {
      scents.value[index] = { ...scents.value[index], ...updates }
      return scents.value[index]
    }
    return null
  }

  const deleteScent = (id) => {
    const scent = scents.value.find(s => s.id === id)
    if (scent) {
      scent.archivedAt = new Date().toISOString().split('T')[0]
      return true
    }
    return false
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
    getScent,
    addScent,
    updateScent,
    deleteScent,
    setSearchQuery,
    setFilterNoteType
  }
})
