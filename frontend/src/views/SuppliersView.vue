<template>
  <div class="suppliers-view">
    <div class="view-header">
      <h2>🏢 Suppliers</h2>
      <p>Manage ingredient suppliers and contact information</p>
    </div>

    <div class="toolbar">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search suppliers..."
          @input="updateSearch"
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
        + Add Supplier
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
      <table class="suppliers-table">
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
            <th>Company Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Website</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="supplier in sortedSuppliers" :key="supplier.id">
            <td v-if="canDelete" class="checkbox-cell">
              <input
                type="checkbox"
                :checked="selectedIds.has(supplier.id)"
                @change="toggleSelect(supplier.id)"
              />
            </td>
            <td class="supplier-name">{{ supplier.name }}</td>
            <td>
              <a :href="`mailto:${supplier.contactInfo}`" class="link">
                {{ supplier.contactInfo }}
              </a>
            </td>
            <td>{{ supplier.phone || '—' }}</td>
            <td>
              <a
                v-if="supplier.website"
                :href="supplier.website"
                target="_blank"
                class="link"
                title="Visit website"
              >
                🌐 Visit
              </a>
              <span v-else class="no-link">—</span>
            </td>
            <td class="actions">
              <button
                v-if="canEdit"
                class="action-btn edit"
                @click="openEditModal(supplier)"
                title="Edit"
              >
                ✏️
              </button>
              <button
                v-if="canDelete"
                class="action-btn delete"
                @click="openDeleteConfirm(supplier)"
                title="Delete"
              >
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="sortedSuppliers.length === 0" class="empty-state">
        <p>No suppliers found.</p>
      </div>
    </div>

    <!-- Modals -->
    <SupplierModal
      :is-open="supplierModalOpen"
      :supplier="selectedSupplier"
      @close="supplierModalOpen = false"
      @submit="handleSupplierSubmit"
    />

    <ConfirmDialog
      :is-open="confirmDialogOpen"
      :title="`Delete '${selectedSupplier?.name}'?`"
      message="This supplier will be permanently deleted."
      confirm-text="Delete Supplier"
      @close="confirmDialogOpen = false"
      @confirm="handleDeleteSupplier"
    />

    <ConfirmDialog
      :is-open="bulkDeleteConfirmOpen"
      :title="`Delete ${selectedIds.size} supplier(s)?`"
      message="These suppliers will be permanently deleted."
      confirm-text="Delete All"
      @close="bulkDeleteConfirmOpen = false"
      @confirm="handleBulkDeleteSuppliers"
    />

    <Toast :message="toastMessage" :type="toastType" :visible="toastVisible" @close="toastVisible = false" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useSupplierStore } from '../stores/suppliers'
import SupplierModal from '../components/SupplierModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import Toast from '../components/Toast.vue'

const authStore = useAuthStore()
const supplierStore = useSupplierStore()

const searchQuery = ref('')
const sortBy = ref('name-asc')
const supplierModalOpen = ref(false)
const confirmDialogOpen = ref(false)
const bulkDeleteConfirmOpen = ref(false)
const selectedSupplier = ref(null)
const selectedIds = ref(new Set())
const toastVisible = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

const filteredSuppliers = computed(() => {
  if (!searchQuery.value) return supplierStore.suppliers
  const query = searchQuery.value.toLowerCase()
  return supplierStore.suppliers.filter(
    s => s.name.toLowerCase().includes(query) ||
         s.contactInfo.toLowerCase().includes(query)
  )
})

const sortedSuppliers = computed(() => {
  const sorted = [...filteredSuppliers.value]
  
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
  return sortedSuppliers.value.length > 0 && 
         sortedSuppliers.value.every(s => selectedIds.value.has(s.id))
})

const someSelected = computed(() => {
  return selectedIds.value.size > 0 && !allSelected.value
})

const canEdit = computed(() => {
  return ['admin', 'manager'].includes(authStore.user?.role)
})

const canDelete = computed(() => {
  return ['admin'].includes(authStore.user?.role)
})

const updateSearch = () => {
  // Computed property handles filtering
}

const openCreateModal = () => {
  selectedSupplier.value = null
  supplierModalOpen.value = true
}

const openEditModal = (supplier) => {
  selectedSupplier.value = supplier
  supplierModalOpen.value = true
}

const openDeleteConfirm = (supplier) => {
  selectedSupplier.value = supplier
  confirmDialogOpen.value = true
}

const handleSupplierSubmit = (data) => {
  try {
    if (selectedSupplier.value) {
      supplierStore.updateSupplier(selectedSupplier.value.id, data)
      toastMessage.value = `✏️ Supplier "${data.name}" updated successfully`
    } else {
      supplierStore.addSupplier(data)
      toastMessage.value = `✅ Supplier "${data.name}" added successfully`
    }
    toastType.value = 'success'
    toastVisible.value = true
    supplierModalOpen.value = false
    selectedSupplier.value = null
  } catch (err) {
    console.error('Error submitting supplier:', err)
    toastMessage.value = 'Error saving supplier'
    toastType.value = 'error'
    toastVisible.value = true
  }
}

const handleDeleteSupplier = () => {
  try {
    const supplierName = selectedSupplier.value.name
    supplierStore.deleteSupplier(selectedSupplier.value.id)
    toastMessage.value = `🗑️ Supplier "${supplierName}" deleted successfully`
    toastType.value = 'success'
    toastVisible.value = true
    confirmDialogOpen.value = false
    selectedSupplier.value = null
  } catch (err) {
    console.error('Error deleting supplier:', err)
    toastMessage.value = 'Error deleting supplier'
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
    sortedSuppliers.value.forEach(s => selectedIds.value.add(s.id))
  }
}

const openBulkDeleteConfirm = () => {
  bulkDeleteConfirmOpen.value = true
}

const handleBulkDeleteSuppliers = async () => {
  try {
    const count = selectedIds.value.size
    await supplierStore.bulkDeleteSuppliers(Array.from(selectedIds.value))
    toastMessage.value = `🗑️ ${count} supplier(s) deleted successfully`
    toastType.value = 'success'
    toastVisible.value = true
    selectedIds.value.clear()
    bulkDeleteConfirmOpen.value = false
  } catch (err) {
    console.error('Bulk delete error:', err)
    toastMessage.value = 'Error deleting suppliers'
    toastType.value = 'error'
    toastVisible.value = true
  }
}
</script>

<style scoped>
.suppliers-view {
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

.filters {
  display: flex;
  gap: 8px;
}

.filters select,
.sort-select {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filters select:focus,
.sort-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.suppliers-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.suppliers-table thead {
  background: #f8f9fa;
  border-bottom: 1px solid #ddd;
}

.suppliers-table th {
  padding: 12px 16px;
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

.suppliers-table tbody tr {
  border-bottom: 1px solid #eee;
  transition: background 0.2s ease;
}

.suppliers-table tbody tr:hover {
  background: #f9f9f9;
}

.suppliers-table td {
  padding: 12px 16px;
}

.supplier-name {
  font-weight: 600;
  color: #667eea;
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

  .suppliers-table {
    font-size: 12px;
  }

  .suppliers-table th,
  .suppliers-table td {
    padding: 8px 12px;
  }
}
</style>
