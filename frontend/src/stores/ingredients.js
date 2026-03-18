import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useIngredientStore = defineStore('ingredients', () => {
  const ingredients = ref([
    {
      id: 1,
      name: 'Rose Oil',
      supplierId: 1,
      supplierName: 'Global Florals Inc',
      cost: 45.99,
      link: 'https://www.globalflorals.com/rose-oil',
      storageLocation: 'Rack A1',
      createdAt: '2025-01-20'
    },
    {
      id: 2,
      name: 'Bergamot Oil',
      supplierId: 2,
      supplierName: 'Citrus Trading Co',
      cost: 32.50,
      link: 'https://www.citrustrading.com/bergamot',
      storageLocation: 'Rack B2',
      createdAt: '2025-01-22'
    },
    {
      id: 3,
      name: 'Sandalwood Oil',
      supplierId: 1,
      supplierName: 'Global Florals Inc',
      cost: 89.99,
      link: 'https://www.globalflorals.com/sandalwood',
      storageLocation: 'Rack A3',
      createdAt: '2025-02-01'
    }
  ])

  const searchQuery = ref('')
  const filterSupplierId = ref('')

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

  const addIngredient = (ingredient) => {
    const newIngredient = {
      id: Math.max(...ingredients.value.map(i => i.id), 0) + 1,
      ...ingredient,
      createdAt: new Date().toISOString().split('T')[0]
    }
    ingredients.value.push(newIngredient)
    return newIngredient
  }

  const updateIngredient = (id, updates) => {
    const index = ingredients.value.findIndex(i => i.id === id)
    if (index !== -1) {
      ingredients.value[index] = { ...ingredients.value[index], ...updates }
      return ingredients.value[index]
    }
    return null
  }

  const deleteIngredient = (id) => {
    const index = ingredients.value.findIndex(i => i.id === id)
    if (index !== -1) {
      ingredients.value.splice(index, 1)
      return true
    }
    return false
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
    getIngredient,
    addIngredient,
    updateIngredient,
    deleteIngredient,
    setSearchQuery,
    setFilterSupplier
  }
})
