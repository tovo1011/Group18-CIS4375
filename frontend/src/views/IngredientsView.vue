<template>
  <div class="ingredients-view">
    <div class="view-header">
      <h2>🧪 Ingredients</h2>
      <p>Manage ingredients, suppliers, costs, and storage</p>
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

      <button v-if="canEdit" class="btn btn-primary" @click="openCreateModal">
        + Add Ingredient
      </button>
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
              <button
                v-if="canEdit"
                class="action-btn edit"
                @click="openEditModal(ingredient)"
                title="Edit"
              >
                ✏️
              </button>
              <button
                v-if="canDelete"
                class="action-btn delete"
                @click="openDeleteConfirm(ingredient)"
                title="Delete"
              >
                🗑️
              </button>
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
.ingredients-view {
  padding: 30px;
}

.view-header {
  margin-bottom: 30px;
}

.view-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #333;
}

.view-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  align-items: center;
}

.search-bar {
  flex: 1;
  min-width: 200px;
  position: relative;
}

.search-bar input {
  width: 100%;
  padding: 10px 36px 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-bar input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.filters select {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filters select:focus {
  outline: none;
  border-color: #667eea;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ingredients-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.ingredients-table thead {
  background: #f8f9fa;
  border-bottom: 1px solid #ddd;
}

.ingredients-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
}

.ingredients-table tbody tr {
  border-bottom: 1px solid #eee;
  transition: background 0.2s ease;
}

.ingredients-table tbody tr:hover {
  background: #f9f9f9;
}

.ingredients-table td {
  padding: 12px 16px;
}

.ingredient-name {
  font-weight: 600;
  color: #667eea;
}

.cost {
  font-weight: 600;
  color: #27ae60;
}

.link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.2s ease;
}

.link:hover {
  color: #5568d3;
  text-decoration: underline;
}

.no-link {
  color: #ccc;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 8px;
  border: none;
  border-radius: 4px;
  background: #f0f0f0;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #e0e0e0;
}

.action-btn.delete:hover {
  background: #ffebee;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #999;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
  }

  .search-bar {
    width: 100%;
  }

  .ingredients-table {
    font-size: 12px;
  }

  .ingredients-table th,
  .ingredients-table td {
    padding: 8px 12px;
  }
}
</style>
