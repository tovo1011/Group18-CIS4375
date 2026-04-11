<template>
  <ConfirmDialog 
    v-if="visible"
    title="Review & Adjust Scent Notes"
    :show-cancel="true"
    cancel-text="Cancel"
    confirm-text="Import Scents"
    @confirm="handleImport"
    @cancel="handleCancel"
    :large="true"
  >
    <div class="scent-categorizer">
      <div class="instructions">
        <p>✨ Preview of how your scents will be categorized. Drag ingredients between columns or use buttons to adjust.</p>
      </div>

      <div v-if="previewState === 'loading'" class="loading-state">
        <p>🔍 Analyzing categorization...</p>
      </div>

      <div v-else-if="previewState === 'error'" class="error-state">
        <p>❌ {{ previewError }}</p>
      </div>

      <div v-else class="scents-list">
        <!-- Summary Stats -->
        <div class="summary-stats">
          <div class="stat">
            <span class="stat-value">{{ scents.length }}</span>
            <span class="stat-label">Total Scents</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ totalIngredients }}</span>
            <span class="stat-label">Ingredients</span>
          </div>
        </div>

        <!-- Each Scent -->
        <div v-for="(scent, idx) in scents" :key="idx" class="scent-card">
          <div class="scent-header">
            <span class="scent-name">{{ scent.name }}</span>
            <span class="scent-index">{{ idx + 1 }} / {{ scents.length }}</span>
          </div>

          <!-- Scent Notes Columns -->
          <div class="notes-container">
            <!-- Top Notes -->
            <div class="notes-column top-notes">
              <div class="column-header">🔝 Top Notes</div>
              <div 
                class="notes-list"
                @dragover.prevent
                @drop="onDrop($event, idx, 'topNotes')"
              >
                <div 
                  v-for="(ingredient, i) in getNotes(scent, 'topNotes')"
                  :key="`top-${i}`"
                  class="ingredient-tag"
                  draggable="true"
                  @dragstart="onDragStart($event, idx, 'topNotes', i)"
                >
                  <span class="ingredient-text">{{ ingredient }}</span>
                  <div class="ingredient-buttons">
                    <button 
                      v-if="getNotes(scent, 'middleNotes').length > 0 || getNotes(scent, 'baseNotes').length > 0"
                      @click="moveIngredient(idx, 'topNotes', i, 'middleNotes')"
                      title="Move to Middle"
                      class="move-btn"
                    >↓</button>
                  </div>
                </div>
                <div v-if="getNotes(scent, 'topNotes').length === 0" class="empty-state">
                  Drop here
                </div>
              </div>
            </div>

            <!-- Middle Notes -->
            <div class="notes-column middle-notes">
              <div class="column-header">💫 Middle Notes</div>
              <div 
                class="notes-list"
                @dragover.prevent
                @drop="onDrop($event, idx, 'middleNotes')"
              >
                <div 
                  v-for="(ingredient, i) in getNotes(scent, 'middleNotes')"
                  :key="`middle-${i}`"
                  class="ingredient-tag"
                  draggable="true"
                  @dragstart="onDragStart($event, idx, 'middleNotes', i)"
                >
                  <span class="ingredient-text">{{ ingredient }}</span>
                  <div class="ingredient-buttons">
                    <button 
                      v-if="getNotes(scent, 'topNotes').length > 0"
                      @click="moveIngredient(idx, 'middleNotes', i, 'topNotes')"
                      title="Move to Top"
                      class="move-btn"
                    >↑</button>
                    <button 
                      v-if="getNotes(scent, 'baseNotes').length > 0"
                      @click="moveIngredient(idx, 'middleNotes', i, 'baseNotes')"
                      title="Move to Base"
                      class="move-btn"
                    >↓</button>
                  </div>
                </div>
                <div v-if="getNotes(scent, 'middleNotes').length === 0" class="empty-state">
                  Drop here
                </div>
              </div>
            </div>

            <!-- Base Notes -->
            <div class="notes-column base-notes">
              <div class="column-header">🔻 Base Notes</div>
              <div 
                class="notes-list"
                @dragover.prevent
                @drop="onDrop($event, idx, 'baseNotes')"
              >
                <div 
                  v-for="(ingredient, i) in getNotes(scent, 'baseNotes')"
                  :key="`base-${i}`"
                  class="ingredient-tag"
                  draggable="true"
                  @dragstart="onDragStart($event, idx, 'baseNotes', i)"
                >
                  <span class="ingredient-text">{{ ingredient }}</span>
                  <div class="ingredient-buttons">
                    <button 
                      v-if="getNotes(scent, 'middleNotes').length > 0"
                      @click="moveIngredient(idx, 'baseNotes', i, 'middleNotes')"
                      title="Move to Middle"
                      class="move-btn"
                    >↑</button>
                  </div>
                </div>
                <div v-if="getNotes(scent, 'baseNotes').length === 0" class="empty-state">
                  Drop here
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </ConfirmDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ConfirmDialog from './ConfirmDialog.vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const props = defineProps({
  visible: Boolean,
  parsedScents: Array
})

const emit = defineEmits(['import', 'cancel'])

const scents = ref([])
const previewState = ref('loading')
const previewError = ref('')
const dragState = ref({ scentIdx: null, fromCategory: null, ingredientIdx: null })

onMounted(async () => {
  if (props.parsedScents && props.parsedScents.length > 0) {
    await generatePreview()
  }
})

const generatePreview = async () => {
  previewState.value = 'loading'
  previewError.value = ''
  
  try {
    const response = await axios.post(
      `${API_URL}/scents/preview-import`,
      { scents: props.parsedScents },
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      }
    )
    scents.value = response.data.scents
    previewState.value = 'ready'
  } catch (err) {
    previewError.value = err.response?.data?.error || err.message
    previewState.value = 'error'
  }
}

const getNotes = (scent, category) => {
  if (!scent[category]) return []
  return scent[category].split(',').map(n => n.trim()).filter(n => n)
}

const onDragStart = (e, scentIdx, category, ingredientIdx) => {
  dragState.value = { scentIdx, fromCategory: category, ingredientIdx }
  e.dataTransfer.effectAllowed = 'move'
}

const onDrop = (e, scentIdx, toCategory) => {
  e.preventDefault()
  
  const { scentIdx: fromScentIdx, fromCategory, ingredientIdx } = dragState.value
  
  if (fromScentIdx === scentIdx && fromCategory === toCategory) return
  
  if (fromScentIdx === scentIdx) {
    moveIngredient(scentIdx, fromCategory, ingredientIdx, toCategory)
  }
}

const moveIngredient = (scentIdx, fromCategory, ingredientIdx, toCategory) => {
  const scent = scents.value[scentIdx]
  
  const fromNotes = getNotes(scent, fromCategory)
  if (ingredientIdx < 0 || ingredientIdx >= fromNotes.length) return
  
  const ingredient = fromNotes[ingredientIdx]
  
  // Remove from source
  const updatedFromNotes = fromNotes.filter((_, i) => i !== ingredientIdx)
  scent[fromCategory] = updatedFromNotes.length > 0 ? updatedFromNotes.join(', ') : ''
  
  // Add to destination
  const toNotes = getNotes(scent, toCategory)
  scent[toCategory] = toNotes.length > 0 ? [...toNotes, ingredient].join(', ') : ingredient
  
  dragState.value = { scentIdx: null, fromCategory: null, ingredientIdx: null }
}

const totalIngredients = computed(() => {
  return scents.value.reduce((sum, scent) => {
    return sum + 
      getNotes(scent, 'topNotes').length +
      getNotes(scent, 'middleNotes').length +
      getNotes(scent, 'baseNotes').length
  }, 0)
})

const handleImport = () => {
  // Convert back to format needed for backend
  const readyScents = scents.value.map(s => ({
    name: s.name,
    topNotes: s.topNotes,
    middleNotes: s.middleNotes,
    baseNotes: s.baseNotes,
    allNotes: s.allNotes,
    essentialOils: s.essentialOils
  }))
  
  emit('import', readyScents)
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.scent-categorizer {
  padding: 24px 0;
  max-height: 70vh;
  overflow-y: auto;
}

.instructions {
  background: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 24px;
  font-size: 14px;
  color: #0369a1;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.error-state {
  color: #dc2626;
}

.summary-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #1f2937;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.scent-card {
  background: #fafafa;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.scent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f3f4f6;
}

.scent-name {
  font-weight: 600;
  font-size: 15px;
  color: #1f2937;
}

.scent-index {
  font-size: 12px;
  color: #9ca3af;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
}

.notes-container {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}

@media (max-width: 768px) {
  .notes-container {
    grid-template-columns: 1fr;
  }
}

.notes-column {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.column-header {
  font-weight: 600;
  font-size: 13px;
  padding: 12px;
  border-bottom: 2px solid #f3f4f6;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.top-notes .column-header {
  background: #fff7ed;
  border-bottom-color: #fed7aa;
}

.middle-notes .column-header {
  background: #fdf2f8;
  border-bottom-color: #fbcfe8;
}

.base-notes .column-header {
  background: #f0fdf4;
  border-bottom-color: #bbf7d0;
}

.notes-list {
  min-height: 120px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state {
  color: #c5d9f1;
  font-size: 13px;
  text-align: center;
  padding: 24px 0;
  font-style: italic;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ingredient-tag {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 8px 10px;
  font-size: 13px;
  cursor: move;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  user-select: none;
}

.ingredient-tag:hover {
  background: #f9fafb;
  border-color: #9ca3af;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.ingredient-tag:active {
  opacity: 0.7;
}

.ingredient-text {
  flex: 1;
  word-break: break-word;
}

.ingredient-buttons {
  display: flex;
  gap: 4px;
}

.move-btn {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  width: 24px;
  height: 24px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  padding: 0;
}

.move-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.move-btn:active {
  transform: scale(0.95);
}

.scents-list {
  flex: 1;
  overflow-y: auto;
}
</style>
