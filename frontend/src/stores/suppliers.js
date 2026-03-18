import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSupplierStore = defineStore('suppliers', () => {
  const suppliers = ref([
    {
      id: 1,
      name: 'Global Florals Inc',
      contactInfo: 'contact@globalflorals.com',
      website: 'https://www.globalflorals.com',
      phone: '+1-800-555-0101',
      createdAt: '2025-01-15'
    },
    {
      id: 2,
      name: 'Citrus Trading Co',
      contactInfo: 'sales@citrustrading.com',
      website: 'https://www.citrustrading.com',
      phone: '+1-800-555-0102',
      createdAt: '2025-01-20'
    },
    {
      id: 3,
      name: 'Essence Importers Ltd',
      contactInfo: 'info@essenceimporters.com',
      website: 'https://www.essenceimporters.com',
      phone: '+1-800-555-0103',
      createdAt: '2025-02-01'
    }
  ])

  const getSupplier = (id) => {
    return suppliers.value.find(s => s.id === id)
  }

  const addSupplier = (supplier) => {
    const newSupplier = {
      id: Math.max(...suppliers.value.map(s => s.id), 0) + 1,
      ...supplier,
      createdAt: new Date().toISOString().split('T')[0]
    }
    suppliers.value.push(newSupplier)
    return newSupplier
  }

  const updateSupplier = (id, updates) => {
    const index = suppliers.value.findIndex(s => s.id === id)
    if (index !== -1) {
      suppliers.value[index] = { ...suppliers.value[index], ...updates }
      return suppliers.value[index]
    }
    return null
  }

  const deleteSupplier = (id) => {
    const index = suppliers.value.findIndex(s => s.id === id)
    if (index !== -1) {
      suppliers.value.splice(index, 1)
      return true
    }
    return false
  }

  return {
    suppliers,
    getSupplier,
    addSupplier,
    updateSupplier,
    deleteSupplier
  }
})
