<template>
  <div class="scent-library">
    <div class="view-header">
      <h2>🌹 Scent Library</h2>
      <p>Manage fragrance formulas, ingredients, and notes</p>
    </div>

    <div class="toolbar">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search scents by name..."
          @input="scentStore.setSearchQuery(searchQuery)"
        />
        <span class="search-icon">🔍</span>
      </div>

      <div class="filters">
        <select v-model="noteFilter" @change="scentStore.setFilterNoteType(noteFilter)">
          <option value="">All Notes</option>
          <option value="Rose">Rose</option>
          <option value="Bergamot">Bergamot</option>
          <option value="Jasmine">Jasmine</option>
          <option value="Sandalwood">Sandalwood</option>
        </select>
      </div>

      <button v-if="canEdit" class="btn btn-primary" @click="openCreateModal">
        + New Scent
      </button>
    </div>

    <div class="table-container">
      <table class="scents-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Top Notes</th>
            <th>Middle Notes</th>
            <th>Base Notes</th>
            <th>Created By</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="scent in scentStore.filteredScents" :key="scent.id" class="scent-row">
            <td class="scent-name">{{ scent.name }}</td>
            <td class="notes">{{ scent.topNotes }}</td>
            <td class="notes">{{ scent.middleNotes }}</td>
            <td class="notes">{{ scent.baseNotes }}</td>
            <td class="created-by">{{ scent.createdBy }}</td>
            <td class="date">{{ scent.createdAt }}</td>
            <td class="actions">
              <button
                v-if="canEdit"
                class="action-btn edit"
                @click="openEditModal(scent)"
                title="Edit"
              >
                ✏️
              </button>
              <button
                v-if="canDelete"
                class="action-btn delete"
                @click="openDeleteConfirm(scent)"
                title="Delete"
              >
                🗑️
              </button>
              <button
                class="action-btn view"
                @click="viewScent(scent)"
                title="View Details"
              >
                👁️
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="scentStore.filteredScents.length === 0" class="empty-state">
        <p>No scents found. Create your first scent formula!</p>
      </div>
    </div>

    <!-- Modals -->
    <ScentModal
      :is-open="scentModalOpen"
      :scent="selectedScent"
      @close="scentModalOpen = false"
      @submit="handleScentSubmit"
    />

    <ConfirmDialog
      :is-open="confirmDialogOpen"
      :title="`Delete '${selectedScent?.name}'?`"
      message="This scent will be archived and cannot be easily recovered. This action is logged in the audit trail."
      confirm-text="Archive Scent"
      @close="confirmDialogOpen = false"
      @confirm="handleDeleteScent"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useScentStore } from '../stores/scents'
import { useAuditStore } from '../stores/audit'
import ScentModal from '../components/ScentModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const authStore = useAuthStore()
const scentStore = useScentStore()
const auditStore = useAuditStore()

const searchQuery = ref('')
const noteFilter = ref('')
const scentModalOpen = ref(false)
const confirmDialogOpen = ref(false)
const selectedScent = ref(null)

const canEdit = computed(() => {
  return ['admin', 'manager'].includes(authStore.user?.role)
})

const canDelete = computed(() => {
  return ['admin', 'manager'].includes(authStore.user?.role)
})

const openCreateModal = () => {
  selectedScent.value = null
  scentModalOpen.value = true
}

const openEditModal = (scent) => {
  selectedScent.value = scent
  scentModalOpen.value = true
}

const openDeleteConfirm = (scent) => {
  selectedScent.value = scent
  confirmDialogOpen.value = true
}

const viewScent = (scent) => {
  console.log('View details:', scent)
  // Can expand to show a detail view modal later
}

const handleScentSubmit = (data) => {
  if (selectedScent.value) {
    scentStore.updateScent(selectedScent.value.id, data)
    auditStore.addAuditLog({
      userId: authStore.user.id,
      userName: authStore.user.email,
      action: 'UPDATE',
      tableName: 'scents',
      recordId: selectedScent.value.id,
      recordName: selectedScent.value.name,
      details: `Updated scent formula: ${selectedScent.value.name}`
    })
  } else {
    const newScent = scentStore.addScent(data)
    auditStore.addAuditLog({
      userId: authStore.user.id,
      userName: authStore.user.email,
      action: 'CREATE',
      tableName: 'scents',
      recordId: newScent.id,
      recordName: newScent.name,
      details: `Created new scent formula: ${newScent.name}`
    })
  }
  scentModalOpen.value = false
  selectedScent.value = null
}

const handleDeleteScent = () => {
  scentStore.deleteScent(selectedScent.value.id)
  auditStore.addAuditLog({
    userId: authStore.user.id,
    userName: authStore.user.email,
    action: 'DELETE',
    tableName: 'scents',
    recordId: selectedScent.value.id,
    recordName: selectedScent.value.name,
    details: `Archived scent formula: ${selectedScent.value.name}`
  })
  confirmDialogOpen.value = false
  selectedScent.value = null
}
</script>

<style scoped>
.scent-library {
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

.scents-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.scents-table thead {
  background: #f8f9fa;
  border-bottom: 1px solid #ddd;
}

.scents-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
}

.scents-table tbody tr {
  border-bottom: 1px solid #eee;
  transition: background 0.2s ease;
}

.scents-table tbody tr:hover {
  background: #f9f9f9;
}

.scents-table td {
  padding: 12px 16px;
}

.scent-name {
  font-weight: 600;
  color: #667eea;
}

.notes {
  color: #666;
  font-size: 13px;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.created-by {
  font-size: 13px;
  color: #999;
}

.date {
  font-size: 13px;
  color: #999;
  white-space: nowrap;
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

  .scents-table {
    font-size: 12px;
  }

  .scents-table th,
  .scents-table td {
    padding: 8px 12px;
  }

  .notes {
    max-width: 100px;
  }
}
</style>
