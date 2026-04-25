<template>
  <div v-if="isOpen" class="overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>{{ product ? 'Edit Product' : 'Add Product' }}</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-row">
          <div class="form-group">
            <label>Product Name *</label>
            <input v-model="form.product_name" type="text" placeholder="e.g. Rose Perfume" required />
          </div>
          <div class="form-group">
            <label>Product Type *</label>
            <input v-model="form.product_type" type="text" placeholder="e.g. Perfume, Candle" required />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Price *</label>
            <input v-model="form.price" type="number" step="0.01" min="0" placeholder="0.00" required />
          </div>
          <div class="form-group">
            <label>Scent <span class="optional">(optional)</span></label>
            <select v-model="form.scent_id">
              <option value="">— None —</option>
              <option v-for="s in scents" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Description <span class="optional">(optional)</span></label>
          <textarea v-model="form.description" rows="2" placeholder="Short product description…" />
        </div>

        <div class="form-group">
          <label>Photo <span class="optional">(optional)</span></label>
          <div class="upload-area">
            <img v-if="imagePreview" :src="imagePreview" class="image-preview" alt="Preview" />
            <div v-else-if="product?.image" class="image-preview-wrap">
              <img :src="backendBase + product.image" class="image-preview" alt="Current photo" />
              <span class="current-label">Current photo</span>
            </div>
            <label class="upload-btn">
              {{ imagePreview || product?.image ? 'Replace Photo' : 'Choose Photo' }}
              <input type="file" accept="image/*" @change="handleFileChange" hidden />
            </label>
            <button v-if="imagePreview" type="button" class="remove-img-btn" @click="clearImage">Remove</button>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancel</button>
          <button type="submit" class="btn btn-primary">
            {{ product ? 'Save Changes' : 'Add Product' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  isOpen: Boolean,
  product: { type: Object, default: null }
})
const emit = defineEmits(['close', 'submit'])

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
const backendBase = API_URL.replace('/api', '')

const scents = ref([])
const imageFile = ref(null)
const imagePreview = ref(null)

const form = ref({
  product_name: '',
  product_type: '',
  price: '',
  scent_id: '',
  description: ''
})

async function loadScents() {
  try {
    const res = await axios.get(`${API_URL}/scents`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('authToken')}` }
    })
    scents.value = res.data
  } catch {
    scents.value = []
  }
}

watch(() => props.isOpen, (open) => {
  if (open) {
    loadScents()
    imageFile.value = null
    imagePreview.value = null
    if (props.product) {
      form.value = {
        product_name: props.product.name || '',
        product_type: props.product.type || '',
        price: props.product.price || '',
        scent_id: props.product.scentId || '',
        description: props.product.description || ''
      }
    } else {
      form.value = { product_name: '', product_type: '', price: '', scent_id: '', description: '' }
    }
  }
})

function handleFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

function clearImage() {
  imageFile.value = null
  imagePreview.value = null
}

function handleSubmit() {
  const fd = new FormData()
  fd.append('product_name', form.value.product_name)
  fd.append('product_type', form.value.product_type)
  fd.append('price', form.value.price)
  fd.append('description', form.value.description)
  if (form.value.scent_id) fd.append('scent_id', form.value.scent_id)
  if (imageFile.value) fd.append('image', imageFile.value)
  emit('submit', fd)
}
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0; background: rgba(44,24,16,0.45);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal {
  background: #fff; border-radius: 12px; width: 520px; max-width: 95vw;
  max-height: 90vh; overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px 0;
}
.modal-header h3 { margin: 0; font-size: 18px; color: #333; }
.close-btn { background: none; border: none; font-size: 16px; cursor: pointer; color: #999; }
.close-btn:hover { color: #333; }
.modal-body { padding: 20px 24px 24px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { margin-bottom: 16px; display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 12px; font-weight: 600; color: #555; text-transform: uppercase; letter-spacing: 0.05em; }
.optional { font-weight: 400; text-transform: none; letter-spacing: 0; color: #aaa; }
.form-group input,
.form-group select,
.form-group textarea {
  padding: 9px 12px; border: 1px solid #ddd; border-radius: 6px;
  font-size: 14px; color: #333; font-family: inherit;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
.form-group textarea { resize: vertical; }
.upload-area { display: flex; flex-direction: column; gap: 10px; }
.image-preview { width: 100%; max-height: 160px; object-fit: cover; border-radius: 8px; border: 1px solid #eee; }
.image-preview-wrap { position: relative; }
.current-label { font-size: 11px; color: #999; margin-top: 4px; display: block; }
.upload-btn {
  display: inline-block; padding: 8px 16px; background: #f0f0f0;
  border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer;
  color: #555; transition: background 0.2s; width: fit-content;
}
.upload-btn:hover { background: #e0e0e0; }
.remove-img-btn {
  background: none; border: none; color: #c0392b; font-size: 12px;
  cursor: pointer; padding: 0; text-align: left; width: fit-content;
}
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 8px; }
.btn { padding: 10px 20px; border: none; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-primary { background: #667eea; color: white; }
.btn-primary:hover { background: #5568d3; }
.btn-secondary { background: #f0f0f0; color: #555; }
.btn-secondary:hover { background: #e0e0e0; }

@media (max-width: 520px) {
  .form-row { grid-template-columns: 1fr; }
}
</style>
