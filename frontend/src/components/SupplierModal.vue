<template>
  <div v-if="isOpen" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEditing ? 'Edit Supplier' : 'Add New Supplier' }}</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="name">Company Name *</label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            placeholder="e.g., Global Florals Inc"
            required
          />
        </div>

        <div class="form-group">
          <label for="contactInfo">Contact Email *</label>
          <input
            id="contactInfo"
            v-model="formData.contactInfo"
            type="email"
            placeholder="contact@example.com"
            required
          />
        </div>

        <div class="form-group">
          <label for="phone">Phone Number</label>
          <input
            id="phone"
            v-model="formData.phone"
            type="tel"
            placeholder="+1-800-555-0000"
          />
        </div>

        <div class="form-group">
          <label for="website">Website</label>
          <input
            id="website"
            v-model="formData.website"
            type="url"
            placeholder="https://www.example.com"
          />
        </div>

        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="close">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary">
            {{ isEditing ? 'Update' : 'Add' }}
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
  supplier: Object
})

const emit = defineEmits(['close', 'submit'])

const isEditing = ref(false)
const formData = ref({
  name: '',
  contactInfo: '',
  phone: '',
  website: ''
})

watch(() => props.isOpen, (newVal) => {
  if (newVal && props.supplier) {
    isEditing.value = true
    formData.value = { ...props.supplier }
  } else if (newVal) {
    isEditing.value = false
    formData.value = {
      name: '',
      contactInfo: '',
      phone: '',
      website: ''
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
