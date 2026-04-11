<template>
  <div class="essential-oils-view">
    <div class="view-header">
      <h2>🧃 Essential Oils</h2>
      <p>Manage essential oils, suppliers, costs, and inventory</p>
    </div>

    <div class="toolbar">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search oils..."
          @input="oilStore.setSearchQuery(searchQuery)"
        />
        <span class="search-icon">🔍</span>
      </div>

      <div class="filters">
        <select v-model="sortBy" class="sort-select">
          <option value="name-asc">Sort: A-Z</option>
          <option value="name-desc">Sort: Z-A</option>
          <option value="date-desc">Sort: Date Added</option>
        </select>
      </div>

      <button v-if="canEdit" class="btn btn-primary" @click="openCreateModal">
        + Add Oil
      </button>

      <button
        v-if="selectedIds.size > 0 && canDelete"
        class="btn btn-danger"
        @click="openBulkDeleteConfirm"
      >
        🗑️ Delete Selected ({{ selectedIds.size }})
      </button>
    </div>

    <div class="table-container">
      <table class="oils-table">
        <thead>
          <tr>
            <th v-if="canDelete" class="checkbox-cell">
              <input
                type="checkbox"
                :checked="allSelected"
                :indeterminate="someSelected"
                @change="toggleSelectAll"
              />
            </th>
            <th>Oil Name</th>
            <th>Supplier</th>
            <th>Unit Cost</th>
            <th>Description</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="oil in sortedOils" :key="oil.id" class="oil-row">
            <td v-if="canDelete" class="checkbox-cell">
              <input
                type="checkbox"
                :checked="selectedIds.has(oil.id)"
                @change="toggleSelect(oil.id)"
              />
            </td>
            <td class="oil-name">{{ oil.name }}</td>
            <td>{{ oil.supplierName }}</td>
            <td class="cost">${{ oil.unitCost.toFixed(2) }}</td>
            <td class="description">{{ oil.description || '—' }}</td>
            <td class="status">
              <span :class="`status-badge ${oil.status?.toLowerCase()}`">
                {{ oil.status || 'active' }}
              </span>
            </td>
            <td class="actions">
              <button
                v-if="canEdit"
                class="action-btn edit"
                @click="openEditModal(oil)"
                title="Edit"
              >
                ✏️
              </button>
              <button
                v-if="canDelete"
                class="action-btn delete"
                @click="openDeleteConfirm(oil)"
                title="Delete"
              >
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="sortedOils.length === 0" class="empty-state">
        <p>No essential oils found. Create your first oil!</p>
      </div>
    </div>

    <!-- Modals -->
    <EssentialOilModal
      :is-open="oilModalOpen"
      :oil="selectedOil"
      @close="oilModalOpen = false"
      @submit="handleOilSubmit"
    />

    <ConfirmDialog
      :is-open="confirmDialogOpen"
      :title="`Delete '${selectedOil?.name}'?`"
      message="This oil will be permanently deleted from the inventory."
      confirm-text="Delete Oil"
      @close="confirmDialogOpen = false"
      @confirm="handleDeleteOil"
    />

    <ConfirmDialog
      :is-open="bulkDeleteConfirmOpen"
      :title="`Delete ${selectedIds.size} oil(s)?`"
      message="These oils will be permanently deleted from the inventory."
      confirm-text="Delete All"
      @close="bulkDeleteConfirmOpen = false"
      @confirm="handleBulkDeleteOils"
    />

    <Toast :message="toastMessage" :type="toastType" :visible="toastVisible" @close="toastVisible = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useEssentialOilStore } from '../stores/essential-oils'
import { useSupplierStore } from '../stores/suppliers'
import EssentialOilModal from '../components/EssentialOilModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import Toast from '../components/Toast.vue'

const authStore = useAuthStore()
const oilStore = useEssentialOilStore()
const supplierStore = useSupplierStore()

const searchQuery = ref('')
const sortBy = ref('name-asc')
const oilModalOpen = ref(false)
const confirmDialogOpen = ref(false)
const bulkDeleteConfirmOpen = ref(false)
const selectedOil = ref(null)
const selectedIds = ref(new Set())
const toastVisible = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

const suppliers = computed(() => supplierStore.suppliers)

const sortedOils = computed(() => {
  const filtered = oilStore.filteredOils
  const sorted = [...filtered]
  
  if (sortBy.value === 'name-asc') {
    sorted.sort((a, b) => a.name.localeCompare(b.name))
  } else if (sortBy.value === 'name-desc') {
    sorted.sort((a, b) => b.name.localeCompare(a.name))
  } else if (sortBy.value === 'date-desc') {
    sorted.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  }
  
  return sorted
})

const allSelected = computed(() => {
  return sortedOils.value.length > 0 && 
         sortedOils.value.every(o => selectedIds.value.has(o.id))
})

const someSelected = computed(() => {
  return selectedIds.value.size > 0 && !allSelected.value
})

const canEdit = computed(() => {
  return ['admin', 'manager'].includes(authStore.user?.role)
})

const canDelete = computed(() => {
  return ['admin', 'manager'].includes(authStore.user?.role)
})

onMounted(async () => {
  await oilStore.fetchOils()
  await supplierStore.fetchSuppliers()
})

const openCreateModal = () => {
  selectedOil.value = null
  oilModalOpen.value = true
}

const openEditModal = (oil) => {
  selectedOil.value = oil
  oilModalOpen.value = true
}

const openDeleteConfirm = (oil) => {
  selectedOil.value = oil
  confirmDialogOpen.value = true
}

const handleOilSubmit = async (data) => {
  try {
    if (selectedOil.value) {
      await oilStore.updateOil(selectedOil.value.id, data)
      toastMessage.value = `✏️ Oil "${data.name}" updated successfully`
    } else {
      await oilStore.addOil(data)
      toastMessage.value = `✅ Oil "${data.name}" added successfully`
    }
    toastType.value = 'success'
    toastVisible.value = true
    oilModalOpen.value = false
    selectedOil.value = null
  } catch (err) {
    console.error('Error submitting oil:', err)
    toastMessage.value = 'Error saving oil'
    toastType.value = 'error'
    toastVisible.value = true
  }
}

const handleDeleteOil = async () => {
  try {
    const oilName = selectedOil.value.name
    await oilStore.deleteOil(selectedOil.value.id)
    toastMessage.value = `🗑️ Oil "${oilName}" deleted successfully`
    toastType.value = 'success'
    toastVisible.value = true
    confirmDialogOpen.value = false
    selectedOil.value = null
  } catch (err) {
    console.error('Error deleting oil:', err)
    toastMessage.value = 'Error deleting oil'
    toastType.value = 'error'
    toastVisible.value = true
  }
}

const toggleSelect = (id) => {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedIds.value.clear()
  } else {
    sortedOils.value.forEach(o => selectedIds.value.add(o.id))
  }
}

const openBulkDeleteConfirm = () => {
  bulkDeleteConfirmOpen.value = true
}

const handleBulkDeleteOils = async () => {
  try {
    const count = selectedIds.value.size
    await oilStore.bulkDeleteOils(Array.from(selectedIds.value))
    toastMessage.value = `🗑️ ${count} oil(s) deleted successfully`
    toastType.value = 'success'
    toastVisible.value = true
    selectedIds.value.clear()
    bulkDeleteConfirmOpen.value = false
  } catch (err) {
    console.error('Bulk delete error:', err)
    toastMessage.value = 'Error deleting oils'
    toastType.value = 'error'
    toastVisible.value = true
  }
}
</script>

<style scoped>
.essential-oils-view {
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
  color: #999;
}

.filters select {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background: white;
}

.filters select:focus,
.sort-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.sort-select {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background: white;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.oils-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.oils-table thead {
  background-color: #f5f5f5;
  border-bottom: 2px solid #ddd;
}

.oils-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
}

.checkbox-cell {
  width: 40px;
  padding: 12px 8px !important;
  text-align: center;
}

.checkbox-cell input[type="checkbox"] {
  cursor: pointer;
}

.oils-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.oils-table tbody tr:hover {
  background-color: #fafafa;
}

.oil-row:hover {
  background-color: #f9f9f9;
}

.oil-name {
  font-weight: 500;
  color: #222;
}

.cost {
  font-weight: 600;
  color: #667eea;
}

.description {
  color: #666;
  font-size: 13px;
}

.status {
  text-align: center;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background-color: #f8d7da;
  color: #721c24;
}

.actions {
  text-align: center;
  width: 100px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px 8px;
  margin: 0 2px;
  transition: opacity 0.2s;
}

.action-btn:hover {
  opacity: 0.7;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: #999;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #667eea;
  color: white;
}

.btn-primary:hover {
  background-color: #5568d3;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}
</style>
