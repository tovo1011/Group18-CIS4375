<template>
  <div class="scent-library">
    <div class="breadcrumb">
      <router-link to="/dashboard" class="bc-back">← Dashboard</router-link>
      <span class="bc-sep">/</span>
      <span class="bc-current">Scent Library</span>
    </div>
    <div class="view-header">
      <div class="view-header-left">
        <h2>Scent Library</h2>
        <p>Manage fragrance formulas, ingredients, and notes</p>
      </div>
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
            <th>Top Notes</th>
            <th>Middle Notes</th>
            <th>Base Notes</th>
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
            <td class="notes">
              <span v-if="scent.topNotes" class="note-pill pill-top">{{ scent.topNotes }}</span>
              <span v-else class="note-empty">—</span>
            </td>
            <td class="notes">
              <span v-if="scent.middleNotes" class="note-pill pill-middle">{{ scent.middleNotes }}</span>
              <span v-else class="note-empty">—</span>
            </td>
            <td class="notes">
              <span v-if="scent.baseNotes" class="note-pill pill-base">{{ scent.baseNotes }}</span>
              <span v-else class="note-empty">—</span>
            </td>
            <td class="created-by">{{ scent.createdBy }}</td>
            <td class="date">{{ scent.createdAt }}</td>
            <td class="actions">
              <button v-if="canEdit" class="action-btn edit" @click="openEditModal(scent)">Edit</button>
              <button class="action-btn view" @click="viewScent(scent)">View</button>
              <button v-if="canDelete" class="action-btn delete" @click="openDeleteConfirm(scent)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="sortedScents.length === 0" class="empty-state">
        <p>No scents found. Create your first scent formula!</p>
      </div>
    </div>

    <!-- View Modal -->
    <div v-if="viewModalOpen" class="modal-overlay" @click="viewModalOpen = false">
      <div class="modal-content view-modal" @click.stop>
        <div class="view-modal-header">
          <div>
            <p class="view-modal-subtitle">Fragrance Profile</p>
            <h2 class="view-modal-title">{{ viewingScent?.name }}</h2>
          </div>
          <button class="close-btn" @click="viewModalOpen = false">&times;</button>
        </div>

        <div class="view-modal-body">
          <!-- Fragrance Pyramid -->
          <div class="pyramid-section">
            <div class="pyramid-tier top-tier">
              <div class="tier-header">
                <span class="tier-dot top-dot"></span>
                <span class="tier-title">Top Notes</span>
                <span class="tier-desc">First impression · evaporates quickly</span>
              </div>
              <div class="tag-list">
                <template v-if="viewingScent?.topNotes">
                  <span v-for="note in viewingScent.topNotes.split(',')" :key="note" class="tag tag-top">{{ note.trim() }}</span>
                </template>
                <span v-else class="tag-empty">—</span>
              </div>
            </div>

            <div class="pyramid-tier middle-tier">
              <div class="tier-header">
                <span class="tier-dot middle-dot"></span>
                <span class="tier-title">Middle Notes</span>
                <span class="tier-desc">Heart of the scent</span>
              </div>
              <div class="tag-list">
                <template v-if="viewingScent?.middleNotes">
                  <span v-for="note in viewingScent.middleNotes.split(',')" :key="note" class="tag tag-middle">{{ note.trim() }}</span>
                </template>
                <span v-else class="tag-empty">—</span>
              </div>
            </div>

            <div class="pyramid-tier base-tier">
              <div class="tier-header">
                <span class="tier-dot base-dot"></span>
                <span class="tier-title">Base Notes</span>
                <span class="tier-desc">Lasting foundation</span>
              </div>
              <div class="tag-list">
                <template v-if="viewingScent?.baseNotes">
                  <span v-for="note in viewingScent.baseNotes.split(',')" :key="note" class="tag tag-base">{{ note.trim() }}</span>
                </template>
                <span v-else class="tag-empty">—</span>
              </div>
            </div>
          </div>

          <!-- Meta info -->
          <div class="view-meta">
            <div v-if="viewingScent?.essentialOils" class="view-meta-row">
              <span class="view-meta-label">Essential Oils</span>
              <span class="view-meta-value">{{ viewingScent.essentialOils }}</span>
            </div>
            <div class="view-meta-row">
              <span class="view-meta-label">Created By</span>
              <span class="view-meta-value">{{ viewingScent?.createdBy }}</span>
            </div>
            <div class="view-meta-row">
              <span class="view-meta-label">Date Added</span>
              <span class="view-meta-value">{{ viewingScent?.createdAt }}</span>
            </div>
          </div>
        </div>
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
const viewModalOpen = ref(false)
const viewingScent = ref(null)
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
  viewingScent.value = scent
  viewModalOpen.value = true
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
  overflow-x: auto;
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
  max-width: 140px;
}

.note-pill {
  display: inline-block;
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 130px;
  vertical-align: middle;
}

.pill-top    { background: #FFF3CD; color: #856404; }
.pill-middle { background: #F8D7DA; color: #842029; }
.pill-base   { background: #D1E7DD; color: #0A3622; }

.note-empty {
  color: #ccc;
  font-size: 13px;
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

/* ── View Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.view-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 24px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.view-modal-subtitle {
  margin: 0 0 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #aaa;
}

.view-modal-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
}

.close-btn {
  background: none;
  border: none;
  font-size: 26px;
  cursor: pointer;
  color: #bbb;
  line-height: 1;
  padding: 0;
}

.close-btn:hover { color: #333; }

.view-modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Pyramid tiers */
.pyramid-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pyramid-tier {
  border-radius: 12px;
  padding: 14px 16px;
}

.top-tier    { background: #FFFBEB; border: 1px solid #FDE68A; }
.middle-tier { background: #FFF1F2; border: 1px solid #FECDD3; }
.base-tier   { background: #F0FDF4; border: 1px solid #BBF7D0; }

.tier-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.tier-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.top-dot    { background: #F59E0B; }
.middle-dot { background: #F43F5E; }
.base-dot   { background: #10B981; }

.tier-title {
  font-size: 13px;
  font-weight: 700;
  color: #333;
}

.tier-desc {
  font-size: 11px;
  color: #aaa;
  margin-left: auto;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  display: inline-block;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
}

.tag-top    { background: #FEF3C7; color: #92400E; }
.tag-middle { background: #FFE4E6; color: #9F1239; }
.tag-base   { background: #DCFCE7; color: #14532D; }

.tag-empty {
  font-size: 13px;
  color: #ccc;
}

/* Meta section */
.view-meta {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.view-meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.view-meta-label {
  font-size: 12px;
  font-weight: 600;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.view-meta-value {
  font-size: 13px;
  color: #555;
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
