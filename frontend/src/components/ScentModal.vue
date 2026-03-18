<template>
  <div v-if="isOpen" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEditing ? 'Edit Scent' : 'Create New Scent' }}</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="name">Scent Name *</label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            placeholder="e.g., Rose Elegance"
            required
          />
        </div>

        <div class="form-group">
          <label for="topNotes">Top Notes *</label>
          <input
            id="topNotes"
            v-model="formData.topNotes"
            type="text"
            placeholder="e.g., Bergamot, Lemon"
            required
          />
        </div>

        <div class="form-group">
          <label for="middleNotes">Middle Notes *</label>
          <input
            id="middleNotes"
            v-model="formData.middleNotes"
            type="text"
            placeholder="e.g., Rose, Jasmine"
            required
          />
        </div>

        <div class="form-group">
          <label for="baseNotes">Base Notes *</label>
          <input
            id="baseNotes"
            v-model="formData.baseNotes"
            type="text"
            placeholder="e.g., Sandalwood, Musk"
            required
          />
        </div>

        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="close">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary">
            {{ isEditing ? 'Update' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  isOpen: Boolean,
  scent: Object
})

const emit = defineEmits(['close', 'submit'])

const isEditing = ref(false)
const formData = ref({
  name: '',
  topNotes: '',
  middleNotes: '',
  baseNotes: '',
  createdBy: 'admin@t4scents.com'
})

watch(() => props.isOpen, (newVal) => {
  if (newVal && props.scent) {
    isEditing.value = true
    formData.value = { ...props.scent }
  } else if (newVal) {
    isEditing.value = false
    formData.value = {
      name: '',
      topNotes: '',
      middleNotes: '',
      baseNotes: '',
      createdBy: 'admin@t4scents.com'
    }
  }
})

const handleSubmit = () => {
  emit('submit', formData.value)
  close()
}

const close = () => {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #999;
}

.close-btn:hover {
  color: #333;
}

.modal-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  flex: 1;
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

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}
</style>
