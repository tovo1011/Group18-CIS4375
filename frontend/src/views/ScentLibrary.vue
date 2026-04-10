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
        <select v-model="noteFilter" @change="scentStore.setFilterNoteType(noteFilter)">
          <option value="">All Notes</option>
          <option value="Rose">Rose</option>
          <option value="Bergamot">Bergamot</option>
          <option value="Jasmine">Jasmine</option>
          <option value="Sandalwood">Sandalwood</option>
        </select>
      </div>

      <button v-if="canEdit" class="btn btn-primary" @click="openCreateModal">+ New Scent</button>
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
              <button v-if="canEdit" class="action-btn edit" @click="openEditModal(scent)">Edit</button>
              <button class="action-btn view" @click="viewScent(scent)">View</button>
              <button v-if="canDelete" class="action-btn delete" @click="openDeleteConfirm(scent)">Delete</button>
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
import { ref, computed, onMounted } from 'vue'
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

onMounted(async () => {
  await scentStore.fetchScents()
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
    } else {
      await scentStore.addScent(data)
    }
    scentModalOpen.value = false
    selectedScent.value = null
  } catch (err) {
    console.error('Error submitting scent:', err)
  }
}

const handleDeleteScent = async () => {
  try {
    await scentStore.deleteScent(selectedScent.value.id)
    confirmDialogOpen.value = false
    selectedScent.value = null
  } catch (err) {
    console.error('Error deleting scent:', err)
  }
}
</script>

<style scoped>
.scent-library { font-family: var(--font-sans); }
.scent-name { font-weight: 600; color: var(--brown); }
.notes { color: var(--brown-lt); max-width: 180px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.created-by, .date { color: var(--brown-lt); white-space: nowrap; }
/* action-btn, btn, toolbar, table-container, empty-state come from global style.css */
</style>
