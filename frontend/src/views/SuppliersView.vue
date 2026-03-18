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

      <button v-if="canEdit" class="btn btn-primary" @click="openCreateModal">
        + Add Supplier
      </button>
    </div>

    <div class="table-container">
      <table class="suppliers-table">
        <thead>
          <tr>
            <th>Company Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Website</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="supplier in filteredSuppliers" :key="supplier.id">
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

      <div v-if="filteredSuppliers.length === 0" class="empty-state">
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
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useSupplierStore } from '../stores/suppliers'
import { useAuditStore } from '../stores/audit'
import SupplierModal from '../components/SupplierModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const authStore = useAuthStore()
const supplierStore = useSupplierStore()
const auditStore = useAuditStore()

const searchQuery = ref('')
const supplierModalOpen = ref(false)
const confirmDialogOpen = ref(false)
const selectedSupplier = ref(null)

const filteredSuppliers = computed(() => {
  if (!searchQuery.value) return supplierStore.suppliers
  const query = searchQuery.value.toLowerCase()
  return supplierStore.suppliers.filter(
    s => s.name.toLowerCase().includes(query) ||
         s.contactInfo.toLowerCase().includes(query)
  )
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
  if (selectedSupplier.value) {
    supplierStore.updateSupplier(selectedSupplier.value.id, data)
    auditStore.addAuditLog({
      userId: authStore.user.id,
      userName: authStore.user.email,
      action: 'UPDATE',
      tableName: 'suppliers',
      recordId: selectedSupplier.value.id,
      recordName: selectedSupplier.value.name,
      details: `Updated supplier: ${selectedSupplier.value.name}`
    })
  } else {
    const newSupplier = supplierStore.addSupplier(data)
    auditStore.addAuditLog({
      userId: authStore.user.id,
      userName: authStore.user.email,
      action: 'CREATE',
      tableName: 'suppliers',
      recordId: newSupplier.id,
      recordName: newSupplier.name,
      details: `Added supplier: ${newSupplier.name}`
    })
  }
  supplierModalOpen.value = false
  selectedSupplier.value = null
}

const handleDeleteSupplier = () => {
  supplierStore.deleteSupplier(selectedSupplier.value.id)
  auditStore.addAuditLog({
    userId: authStore.user.id,
    userName: authStore.user.email,
    action: 'DELETE',
    tableName: 'suppliers',
    recordId: selectedSupplier.value.id,
    recordName: selectedSupplier.value.name,
    details: `Deleted supplier: ${selectedSupplier.value.name}`
  })
  confirmDialogOpen.value = false
  selectedSupplier.value = null
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
