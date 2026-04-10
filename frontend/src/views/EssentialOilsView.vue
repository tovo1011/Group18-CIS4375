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
        <select v-model="supplierFilter" @change="oilStore.setFilterSupplier(supplierFilter)">
          <option value="">All Suppliers</option>
          <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
            {{ supplier.name }}
          </option>
        </select>
      </div>

      <button v-if="canEdit" class="btn btn-primary" @click="openCreateModal">
        + Add Oil
      </button>
    </div>

    <div class="table-container">
      <table class="oils-table">
        <thead>
          <tr>
            <th>Oil Name</th>
            <th>Supplier</th>
            <th>Unit Cost</th>
            <th>Description</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="oil in oilStore.filteredOils" :key="oil.id" class="oil-row">
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

      <div v-if="oilStore.filteredOils.length === 0" class="empty-state">
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useEssentialOilStore } from '../stores/essential-oils'
import { useSupplierStore } from '../stores/suppliers'
import EssentialOilModal from '../components/EssentialOilModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const authStore = useAuthStore()
const oilStore = useEssentialOilStore()
const supplierStore = useSupplierStore()

const searchQuery = ref('')
const supplierFilter = ref('')
const oilModalOpen = ref(false)
const confirmDialogOpen = ref(false)
const selectedOil = ref(null)

const suppliers = computed(() => supplierStore.suppliers)

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
    } else {
      await oilStore.addOil(data)
    }
    oilModalOpen.value = false
    selectedOil.value = null
  } catch (err) {
    console.error('Error submitting oil:', err)
  }
}

const handleDeleteOil = async () => {
  try {
    await oilStore.deleteOil(selectedOil.value.id)
    confirmDialogOpen.value = false
    selectedOil.value = null
  } catch (err) {
    console.error('Error deleting oil:', err)
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
}

.filters select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}
</style>
