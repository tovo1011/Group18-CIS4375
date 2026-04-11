<template>
  <div class="ingredients-view">
    <div class="breadcrumb">
      <router-link to="/dashboard" class="bc-back">← Dashboard</router-link>
      <span class="bc-sep">/</span>
      <span class="bc-current">Ingredients</span>
    </div>
    <div class="view-header">
      <div class="view-header-left">
        <h2>Ingredients</h2>
        <p>Manage ingredients, suppliers, costs, and storage</p>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search ingredients..."
          @input="ingredientStore.setSearchQuery(searchQuery)"
        />
        <span class="search-icon">🔍</span>
      </div>

      <div class="filters">
        <select v-model="supplierFilter" @change="ingredientStore.setFilterSupplier(supplierFilter)">
          <option value="">All Suppliers</option>
          <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
            {{ supplier.name }}
          </option>
        </select>
      </div>

      <button v-if="canEdit" class="btn btn-primary" @click="openCreateModal">+ Add Ingredient</button>
    </div>

    <div class="table-container">
      <table class="ingredients-table">
        <thead>
          <tr>
            <th>Ingredient</th>
            <th>Supplier</th>
            <th>Cost</th>
            <th>Storage Location</th>
            <th>Purchase Link</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ingredient in ingredientStore.filteredIngredients" :key="ingredient.id">
            <td class="ingredient-name">{{ ingredient.name }}</td>
            <td>{{ ingredient.supplierName }}</td>
            <td class="cost">${{ ingredient.cost.toFixed(2) }}</td>
            <td>{{ ingredient.storageLocation || '—' }}</td>
            <td>
              <a
                v-if="ingredient.link"
                :href="ingredient.link"
                target="_blank"
                class="link"
                title="Open supplier link"
              >
                🔗 Link
              </a>
              <span v-else class="no-link">—</span>
            </td>
            <td class="actions">
              <button v-if="canEdit" class="action-btn edit" @click="openEditModal(ingredient)">Edit</button>
              <button v-if="canDelete" class="action-btn delete" @click="openDeleteConfirm(ingredient)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="ingredientStore.filteredIngredients.length === 0" class="empty-state">
        <p>No ingredients found.</p>
      </div>
    </div>

    <!-- Modals -->
    <IngredientModal
      :is-open="ingredientModalOpen"
      :ingredient="selectedIngredient"
      @close="ingredientModalOpen = false"
      @submit="handleIngredientSubmit"
    />

    <ConfirmDialog
      :is-open="confirmDialogOpen"
      :title="`Delete '${selectedIngredient?.name}'?`"
      message="This ingredient will be permanently deleted."
      confirm-text="Delete Ingredient"
      @close="confirmDialogOpen = false"
      @confirm="handleDeleteIngredient"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useIngredientStore } from '../stores/ingredients'
import { useSupplierStore } from '../stores/suppliers'
import IngredientModal from '../components/IngredientModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const authStore = useAuthStore()
const ingredientStore = useIngredientStore()
const supplierStore = useSupplierStore()

const searchQuery = ref('')
const supplierFilter = ref('')
const ingredientModalOpen = ref(false)
const confirmDialogOpen = ref(false)
const selectedIngredient = ref(null)

const suppliers = computed(() => supplierStore.suppliers)

const canEdit = computed(() => {
  return ['admin', 'manager'].includes(authStore.user?.role)
})

const canDelete = computed(() => {
  return ['admin', 'manager'].includes(authStore.user?.role)
})

const openCreateModal = () => {
  selectedIngredient.value = null
  ingredientModalOpen.value = true
}

const openEditModal = (ingredient) => {
  selectedIngredient.value = ingredient
  ingredientModalOpen.value = true
}

const openDeleteConfirm = (ingredient) => {
  selectedIngredient.value = ingredient
  confirmDialogOpen.value = true
}

const handleIngredientSubmit = (data) => {
  if (selectedIngredient.value) {
    ingredientStore.updateIngredient(selectedIngredient.value.id, data)
  } else {
    ingredientStore.addIngredient(data)
  }
  ingredientModalOpen.value = false
  selectedIngredient.value = null
}

const handleDeleteIngredient = () => {
  ingredientStore.deleteIngredient(selectedIngredient.value.id)
  confirmDialogOpen.value = false
  selectedIngredient.value = null
}
</script>

<style scoped>
.ingredients-view { font-family: var(--font-sans); }
.ingredient-name { font-weight: 600; color: var(--brown); }
.cost { font-weight: 600; color: var(--gold-dk); }
.link { color: var(--gold-dk); text-decoration: none; font-size: 12px; font-weight: 500; }
.link:hover { text-decoration: underline; }
.no-link { color: var(--brown-lt); }
</style>
