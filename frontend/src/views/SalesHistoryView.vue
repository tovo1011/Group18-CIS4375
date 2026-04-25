<template>
  <div class="sales-view">
    <div class="breadcrumb">
      <router-link to="/dashboard" class="bc-back">← Dashboard</router-link>
      <span class="bc-sep">/</span>
      <span class="bc-current">Sales History</span>
    </div>

    <div class="view-header">
      <div>
        <h2>Sales History</h2>
        <p>View and filter past transactions</p>
      </div>
    </div>

    <div class="toolbar">
      <div class="filter-group">
        <label>From</label>
        <input v-model="filters.start" type="date" class="date-input" @change="fetchSales" />
      </div>
      <div class="filter-group">
        <label>To</label>
        <input v-model="filters.end" type="date" class="date-input" @change="fetchSales" />
      </div>
      <div class="filter-group">
        <label>Payment</label>
        <select v-model="filters.method" class="method-select" @change="fetchSales">
          <option value="all">All Methods</option>
          <option value="cash">Cash</option>
          <option value="card">Card</option>
          <option value="venmo">Venmo</option>
          <option value="zelle">Zelle</option>
        </select>
      </div>
      <button class="btn btn-secondary" @click="clearFilters">Clear Filters</button>
      <button class="btn btn-primary" @click="exportCSV">Export CSV</button>
    </div>

    <div v-if="loading" class="empty-state">Loading sales…</div>
    <div v-else-if="sales.length === 0" class="empty-state">No sales found for the selected filters.</div>
    <div v-else>
      <div class="table-container">
        <table class="sales-table">
          <thead>
            <tr>
              <th>Order #</th>
              <th>Date</th>
              <th>Customer</th>
              <th>Items</th>
              <th>Total</th>
              <th>Method</th>
              <th>Event</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in sales" :key="s.id">
              <td class="order-id">#{{ s.id }}</td>
              <td>{{ formatDate(s.date) }}</td>
              <td>{{ s.customerName || '—' }}</td>
              <td class="items-cell" :title="s.items">{{ truncate(s.items, 40) }}</td>
              <td class="total">${{ fmt(s.total) }}</td>
              <td>
                <span :class="`method-badge method-${s.paymentMethod}`">{{ s.paymentMethod }}</span>
              </td>
              <td>{{ s.eventName || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="summary-bar">
        <span><strong>{{ sales.length }}</strong> transaction{{ sales.length !== 1 ? 's' : '' }}</span>
        <span class="summary-total">Total Revenue: <strong>${{ fmt(totalRevenue) }}</strong></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const sales = ref([])
const loading = ref(false)

const filters = ref({
  start: '',
  end: '',
  method: 'all'
})

const totalRevenue = computed(() => sales.value.reduce((sum, s) => sum + s.total, 0))

async function fetchSales() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.start) params.start = filters.value.start
    if (filters.value.end) params.end = filters.value.end
    if (filters.value.method !== 'all') params.method = filters.value.method
    const res = await axios.get(`${API_URL}/sales`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('authToken')}` },
      params
    })
    sales.value = res.data
  } catch (e) {
    console.error('Failed to load sales', e)
    sales.value = []
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  filters.value = { start: '', end: '', method: 'all' }
  fetchSales()
}

function fmt(n) { return Number(n || 0).toFixed(2) }

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function truncate(str, len) {
  if (!str) return '—'
  return str.length > len ? str.slice(0, len) + '…' : str
}

function exportCSV() {
  const headers = ['Order #', 'Date', 'Customer', 'Items', 'Total', 'Method', 'Event']
  const rows = sales.value.map(s => [
    s.id,
    s.date ? new Date(s.date).toLocaleDateString() : '',
    s.customerName || '',
    (s.items || '').replace(/,/g, ';'),
    fmt(s.total),
    s.paymentMethod || '',
    s.eventName || ''
  ])
  const csv = [headers, ...rows].map(r => r.map(v => `"${v}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `sales_${new Date().toISOString().slice(0,10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(fetchSales)
</script>

<style scoped>
.sales-view { padding: 30px; }

.view-header { margin-bottom: 30px; }
.view-header h2 { margin: 0 0 8px; font-size: 24px; color: #333; }
.view-header p { margin: 0; color: #666; font-size: 14px; }

.breadcrumb { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; font-size: 13px; }
.bc-back { color: #667eea; text-decoration: none; }
.bc-back:hover { text-decoration: underline; }
.bc-sep { color: #ccc; }
.bc-current { color: #666; }

.toolbar {
  display: flex; gap: 12px; margin-bottom: 24px;
  flex-wrap: wrap; align-items: flex-end;
}
.filter-group { display: flex; flex-direction: column; gap: 4px; }
.filter-group label { font-size: 11px; font-weight: 600; color: #555; text-transform: uppercase; letter-spacing: 0.05em; }
.date-input, .method-select { padding: 9px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.date-input:focus, .method-select:focus { outline: none; border-color: #667eea; }

.btn { padding: 9px 16px; border: none; border-radius: 4px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-primary { background: #667eea; color: white; }
.btn-primary:hover { background: #5568d3; }
.btn-secondary { background: #f0f0f0; color: #555; }
.btn-secondary:hover { background: #e0e0e0; }

.table-container { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.sales-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.sales-table thead { background: #f8f9fa; border-bottom: 1px solid #ddd; }
.sales-table th { padding: 12px 16px; text-align: left; font-weight: 600; color: #333; }
.sales-table tbody tr { border-bottom: 1px solid #eee; transition: background 0.2s; }
.sales-table tbody tr:hover { background: #f9f9f9; }
.sales-table td { padding: 10px 16px; vertical-align: middle; }

.order-id { font-weight: 600; color: #667eea; }
.total { font-weight: 600; }
.items-cell { max-width: 200px; color: #666; font-size: 13px; }

.method-badge {
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  font-size: 12px; font-weight: 600; text-transform: capitalize;
}
.method-cash { background: #e8f5e9; color: #2e7d32; }
.method-card { background: #e3f2fd; color: #1565c0; }
.method-venmo { background: #e8eaf6; color: #3949ab; }
.method-zelle { background: #fce4ec; color: #c62828; }

.summary-bar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 20px; background: #f8f9fa; border-radius: 0 0 8px 8px;
  font-size: 14px; color: #555; border: 1px solid #eee; border-top: none;
}
.summary-total { font-size: 15px; color: #333; }

.empty-state { padding: 60px 20px; text-align: center; color: #999; font-size: 14px; }

@media (max-width: 768px) {
  .toolbar { flex-direction: column; align-items: stretch; }
  .sales-table { font-size: 12px; }
  .sales-table th, .sales-table td { padding: 8px 10px; }
}
</style>
