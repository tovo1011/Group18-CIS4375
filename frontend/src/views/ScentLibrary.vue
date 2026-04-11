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
        <select v-model="sortBy" class="sort-select">
          <option value="name-asc">Sort: A-Z</option>
          <option value="name-desc">Sort: Z-A</option>
          <option value="date-desc">Sort: Date Added</option>
        </select>
      </div>

      <button v-if="canEdit" class="btn btn-primary" @click="openCreateModal">
        + New Scent
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
      <table class="scents-table">
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
            <th>Name</th>
            <th>Fragrance Notes</th>
            <th>Created By</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="scent in sortedScents" :key="scent.id" class="scent-row">
            <td v-if="canDelete" class="checkbox-cell">
              <input
                type="checkbox"
                :checked="selectedIds.has(scent.id)"
                @change="toggleSelect(scent.id)"
              />
            </td>
            <td class="scent-name">{{ scent.name }}</td>
            <td class="notes">{{ scent.allNotes }}</td>
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

      <div v-if="sortedScents.length === 0" class="empty-state">
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

    <ConfirmDialog
      :is-open="bulkDeleteConfirmOpen"
      :title="`Archive ${selectedIds.size} scent(s)?`"
      message="These scents will be archived and cannot be easily recovered."
      confirm-text="Archive All"
      @close="bulkDeleteConfirmOpen = false"
      @confirm="handleBulkDeleteScents"
    />

    <Toast :message="toastMessage" :type="toastType" :visible="toastVisible" @close="toastVisible = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useScentStore } from '../stores/scents'
import ScentModal from '../components/ScentModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import Toast from '../components/Toast.vue'

const authStore = useAuthStore()
const scentStore = useScentStore()

const searchQuery = ref('')
const sortBy = ref('name-asc')
const scentModalOpen = ref(false)
const confirmDialogOpen = ref(false)
const bulkDeleteConfirmOpen = ref(false)
const selectedScent = ref(null)
const selectedIds = ref(new Set())
const toastVisible = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

onMounted(async () => {
  await scentStore.fetchScents()
})

const sortedScents = computed(() => {
  const filtered = scentStore.filteredScents
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
  return sortedScents.value.length > 0 && 
         sortedScents.value.every(s => selectedIds.value.has(s.id))
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

const handleScentSubmit = async (data) => {
  try {
    if (selectedScent.value) {
      await scentStore.updateScent(selectedScent.value.id, data)
      toastMessage.value = `✏️ Scent "${data.name}" updated successfully`
    } else {
      await scentStore.addScent(data)
      toastMessage.value = `✅ Scent "${data.name}" added successfully`
    }
    toastType.value = 'success'
    toastVisible.value = true
    scentModalOpen.value = false
    selectedScent.value = null
  } catch (err) {
    console.error('Error submitting scent:', err)
    toastMessage.value = 'Error saving scent'
    toastType.value = 'error'
    toastVisible.value = true
  }
}

const handleDeleteScent = async () => {
  try {
    const scentName = selectedScent.value.name
    await scentStore.deleteScent(selectedScent.value.id)
    toastMessage.value = `🗑️ Scent "${scentName}" archived successfully`
    toastType.value = 'success'
    toastVisible.value = true
    confirmDialogOpen.value = false
    selectedScent.value = null
  } catch (err) {
    console.error('Error deleting scent:', err)
    toastMessage.value = 'Error archiving scent'
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
    sortedScents.value.forEach(s => selectedIds.value.add(s.id))
  }
}

const openBulkDeleteConfirm = () => {
  bulkDeleteConfirmOpen.value = true
}

const handleBulkDeleteScents = async () => {
  try {
    const count = selectedIds.value.size
    await scentStore.bulkDeleteScents(Array.from(selectedIds.value))
    toastMessage.value = `🗑️ ${count} scent(s) archived successfully`
    toastType.value = 'success'
    toastVisible.value = true
    selectedIds.value.clear()
    bulkDeleteConfirmOpen.value = false
  } catch (err) {
    console.error('Bulk delete error:', err)
    toastMessage.value = 'Error archiving scents'
    toastType.value = 'error'
    toastVisible.value = true
  }
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

.checkbox-cell {
  width: 40px;
  padding: 12px 8px !important;
  text-align: center;
}

.checkbox-cell input[type="checkbox"] {
  cursor: pointer;
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
