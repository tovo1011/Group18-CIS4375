<template>
  <div class="suppliers-view">
    <div class="breadcrumb">
      <router-link to="/dashboard" class="bc-back">← Dashboard</router-link>
      <span class="bc-sep">/</span>
      <span class="bc-current">Suppliers</span>
    </div>
    <div class="view-header">
      <div class="view-header-left">
        <h2>Suppliers</h2>
        <p>Manage ingredient suppliers and contact information</p>
      </div>
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

      <button v-if="canEdit" class="btn btn-primary" @click="openCreateModal">+ Add Supplier</button>
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
              <button v-if="canEdit" class="action-btn edit" @click="openEditModal(supplier)">Edit</button>
              <button v-if="canDelete" class="action-btn delete" @click="openDeleteConfirm(supplier)">Delete</button>
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
.suppliers-view { font-family: var(--font-sans); }
.supplier-name { font-weight: 600; color: var(--brown); }
.link { color: var(--gold-dk); text-decoration: none; font-size: 12px; font-weight: 500; }
.link:hover { text-decoration: underline; }
.no-link { color: var(--brown-lt); }
</style>
