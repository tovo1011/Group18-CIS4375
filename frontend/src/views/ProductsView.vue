<template>
  <div class="products-view">
    <div class="breadcrumb">
      <router-link to="/dashboard" class="bc-back">← Dashboard</router-link>
      <span class="bc-sep">/</span>
      <span class="bc-current">Products</span>
    </div>

    <div class="view-header">
      <div class="view-header-left">
        <h2>Products</h2>
        <p>Manage products available for sale</p>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-bar">
        <input v-model="searchQuery" type="text" placeholder="Search products…" />
        <span class="search-icon">🔍</span>
      </div>
      <div class="filters">
        <select v-model="sortBy" class="sort-select">
          <option value="name-asc">Sort: Name A–Z</option>
          <option value="name-desc">Sort: Name Z–A</option>
          <option value="price-asc">Sort: Price Low–High</option>
          <option value="price-desc">Sort: Price High–Low</option>
          <option value="type-asc">Sort: Type A–Z</option>
        </select>
      </div>
      <button v-if="canEdit" class="btn btn-primary" @click="openCreateModal">+ Add Product</button>
    </div>

    <div class="table-container">
      <table class="products-table">
        <thead>
          <tr>
            <th class="col-photo">Photo</th>
            <th>Name</th>
            <th>Type</th>
            <th>Price</th>
            <th>Scent</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in sortedProducts" :key="p.id">
            <td class="col-photo">
              <img v-if="p.image" :src="backendBase + p.image" class="thumb" :alt="p.name" />
              <span v-else class="no-photo">—</span>
            </td>
            <td class="product-name">{{ p.name }}</td>
            <td>
              <span class="type-badge">{{ p.type }}</span>
            </td>
            <td>${{ fmt(p.price) }}</td>
            <td>{{ p.scentName || '—' }}</td>
            <td class="actions">
              <button v-if="canEdit" class="action-btn edit" @click="openEditModal(p)">Edit</button>
              <button v-if="canDelete" class="action-btn delete" @click="openDeleteConfirm(p)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="productStore.loading" class="empty-state">Loading products…</div>
      <div v-else-if="sortedProducts.length === 0" class="empty-state">No products found.</div>
    </div>

    <ProductModal
      :is-open="modalOpen"
      :product="selectedProduct"
      @close="modalOpen = false"
      @submit="handleSubmit"
    />

    <ConfirmDialog
      :is-open="confirmOpen"
      :title="`Delete '${selectedProduct?.name}'?`"
      message="This product will be permanently deleted."
      confirm-text="Delete Product"
      @close="confirmOpen = false"
      @confirm="handleDelete"
    />

    <Toast :message="toastMessage" :type="toastType" :visible="toastVisible" @close="toastVisible = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useProductStore } from '../stores/products'
import ProductModal from '../components/ProductModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import Toast from '../components/Toast.vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
const backendBase = API_URL.replace('/api', '')

const authStore = useAuthStore()
const productStore = useProductStore()

const searchQuery = ref('')
const sortBy = ref('name-asc')
const modalOpen = ref(false)
const confirmOpen = ref(false)
const selectedProduct = ref(null)
const toastVisible = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

const canEdit = computed(() => ['admin', 'manager'].includes(authStore.user?.role))
const canDelete = computed(() => authStore.user?.role === 'admin')

const filteredProducts = computed(() => {
  if (!searchQuery.value) return productStore.products
  const q = searchQuery.value.toLowerCase()
  return productStore.products.filter(
    p => p.name.toLowerCase().includes(q) || p.type.toLowerCase().includes(q)
  )
})

const sortedProducts = computed(() => {
  const arr = [...filteredProducts.value]
  if (sortBy.value === 'name-asc') arr.sort((a, b) => a.name.localeCompare(b.name))
  else if (sortBy.value === 'name-desc') arr.sort((a, b) => b.name.localeCompare(a.name))
  else if (sortBy.value === 'price-asc') arr.sort((a, b) => a.price - b.price)
  else if (sortBy.value === 'price-desc') arr.sort((a, b) => b.price - a.price)
  else if (sortBy.value === 'type-asc') arr.sort((a, b) => a.type.localeCompare(b.type))
  return arr
})

function fmt(n) { return Number(n || 0).toFixed(2) }

function openCreateModal() {
  selectedProduct.value = null
  modalOpen.value = true
}

function openEditModal(p) {
  selectedProduct.value = p
  modalOpen.value = true
}

function openDeleteConfirm(p) {
  selectedProduct.value = p
  confirmOpen.value = true
}

async function handleSubmit(formData) {
  try {
    if (selectedProduct.value) {
      await productStore.updateProduct(selectedProduct.value.id, formData)
      showToast(`Product "${formData.get('product_name')}" updated`, 'success')
    } else {
      await productStore.addProduct(formData)
      showToast(`Product "${formData.get('product_name')}" added`, 'success')
    }
    modalOpen.value = false
    selectedProduct.value = null
  } catch {
    showToast('Error saving product', 'error')
  }
}

async function handleDelete() {
  try {
    const name = selectedProduct.value.name
    await productStore.deleteProduct(selectedProduct.value.id)
    showToast(`Product "${name}" deleted`, 'success')
    confirmOpen.value = false
    selectedProduct.value = null
  } catch {
    showToast('Error deleting product', 'error')
  }
}

function showToast(msg, type) {
  toastMessage.value = msg
  toastType.value = type
  toastVisible.value = true
}

onMounted(() => productStore.fetchProducts())
</script>

<style scoped>
.products-view { padding: 30px; }

.view-header { margin-bottom: 30px; }
.view-header h2 { margin: 0 0 8px; font-size: 24px; color: #333; }
.view-header p { margin: 0; color: #666; font-size: 14px; }

.breadcrumb { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; font-size: 13px; }
.bc-back { color: #667eea; text-decoration: none; }
.bc-back:hover { text-decoration: underline; }
.bc-sep { color: #ccc; }
.bc-current { color: #666; }

.toolbar {
  display: flex; gap: 16px; margin-bottom: 24px;
  flex-wrap: wrap; align-items: center;
}
.search-bar { flex: 1; min-width: 200px; position: relative; }
.search-bar input {
  width: 100%; padding: 10px 36px 10px 12px;
  border: 1px solid #ddd; border-radius: 4px; font-size: 14px;
}
.search-bar input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
.search-icon { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; }
.sort-select { padding: 10px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }

.btn { padding: 10px 16px; border: none; border-radius: 4px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-primary { background: #667eea; color: white; }
.btn-primary:hover { background: #5568d3; }

.table-container { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.products-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.products-table thead { background: #f8f9fa; border-bottom: 1px solid #ddd; }
.products-table th { padding: 12px 16px; text-align: left; font-weight: 600; color: #333; }
.products-table tbody tr { border-bottom: 1px solid #eee; transition: background 0.2s; }
.products-table tbody tr:hover { background: #f9f9f9; }
.products-table td { padding: 10px 16px; vertical-align: middle; }

.col-photo { width: 72px; }
.thumb { width: 48px; height: 48px; object-fit: cover; border-radius: 6px; display: block; }
.no-photo { color: #ccc; }

.product-name { font-weight: 600; color: #667eea; }

.type-badge {
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  font-size: 12px; font-weight: 600; background: #f0f4ff; color: #667eea;
}

.actions { display: flex; gap: 8px; }
.action-btn {
  padding: 6px 10px; border: none; border-radius: 4px;
  background: #f0f0f0; cursor: pointer; font-size: 13px; transition: background 0.2s;
}
.action-btn:hover { background: #e0e0e0; }
.action-btn.delete:hover { background: #ffebee; color: #c0392b; }

.empty-state { padding: 60px 20px; text-align: center; color: #999; }

@media (max-width: 768px) {
  .toolbar { flex-direction: column; }
  .search-bar { width: 100%; }
  .products-table { font-size: 12px; }
  .products-table th, .products-table td { padding: 8px 10px; }
  .col-photo { display: none; }
}
</style>
