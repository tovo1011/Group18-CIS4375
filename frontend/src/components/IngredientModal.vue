<template>
  <div v-if="isOpen" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEditing ? 'Edit Ingredient' : 'Create New Ingredient' }}</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="name">Ingredient Name *</label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            placeholder="e.g., Rose Oil"
            required
          />
        </div>

        <div class="form-group">
          <label for="supplier">Supplier *</label>
          <select id="supplier" v-model="formData.supplierId" required>
            <option value="" disabled>Select a supplier</option>
            <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
              {{ supplier.name }}
            </option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="cost">Cost ($) *</label>
            <input
              id="cost"
              v-model.number="formData.cost"
              type="number"
              step="0.01"
              placeholder="0.00"
              required
            />
          </div>

          <div class="form-group">
            <label for="storageLocation">Storage Location</label>
            <input
              id="storageLocation"
              v-model="formData.storageLocation"
              type="text"
              placeholder="e.g., Rack A1"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="link">Supplier Link</label>
          <input
            id="link"
            v-model="formData.link"
            type="url"
            placeholder="https://..."
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
import { useSupplierStore } from '../stores/suppliers'

const props = defineProps({
  isOpen: Boolean,
  ingredient: Object
})

const emit = defineEmits(['close', 'submit'])

const supplierStore = useSupplierStore()

const isEditing = ref(false)
const formData = ref({
  name: '',
  supplierId: '',
  supplierName: '',
  cost: 0,
  storageLocation: '',
  link: ''
})

const suppliers = ref([])

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    suppliers.value = supplierStore.suppliers
    if (props.ingredient) {
      isEditing.value = true
      formData.value = { ...props.ingredient }
    } else {
      isEditing.value = false
      formData.value = {
        name: '',
        supplierId: '',
        supplierName: '',
        cost: 0,
        storageLocation: '',
        link: ''
      }
    }
  }
})

const handleSubmit = () => {
  const supplier = supplierStore.getSupplier(parseInt(formData.value.supplierId))
  const submitData = {
    ...formData.value,
    supplierName: supplier.name
  }
  emit('submit', submitData)
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
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
