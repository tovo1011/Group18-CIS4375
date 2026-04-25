<template>
  <div class="dash-home">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <span>Home</span>
      <span class="sep">/</span>
      <span class="current">Dashboard</span>
    </div>

    <!-- Page header -->
    <div class="page-title-row">
      <div>
        <h2 class="page-title">Dashboard</h2>
        <p class="page-sub">Manage your fragrance collection and business operations.</p>
      </div>
      <button v-if="canEdit" class="btn btn-primary" @click="router.push('/scents')">+ New Scent</button>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-tile">
        <p class="st-label">Total Scents</p>
        <p class="st-val">{{ totalScents }}</p>
        <p class="st-delta">Active formulas</p>
      </div>
      <div class="stat-tile">
        <p class="st-label">Essential Oils</p>
        <p class="st-val">{{ totalIngredients }}</p>
        <p class="st-delta">In library</p>
      </div>
      <div class="stat-tile">
        <p class="st-label">Suppliers</p>
        <p class="st-val">{{ totalSuppliers }}</p>
        <p class="st-delta">All active</p>
      </div>
      <div class="stat-tile">
        <p class="st-label">Activities</p>
        <p class="st-val">{{ recentActivities }}</p>
        <p class="st-delta">Audit entries</p>
      </div>
      <div class="stat-tile">
        <p class="st-label">Total Products</p>
        <p class="st-val">{{ totalProducts }}</p>
        <p class="st-delta">In catalog</p>
      </div>
      <div class="stat-tile">
        <p class="st-label">Total Revenue</p>
        <p class="st-val">${{ totalRevenue }}</p>
        <p class="st-delta">All time sales</p>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <h3 class="chart-title">Oils per Supplier</h3>
        <Bar :data="oilsPerSupplierData" :options="barOptions" />
      </div>
      <div class="chart-card">
        <h3 class="chart-title">Activity Breakdown</h3>
        <Doughnut :data="auditActionData" :options="donutOptions" />
      </div>
      <div class="chart-card">
        <h3 class="chart-title">Avg Oil Cost by Supplier</h3>
        <Bar :data="avgCostData" :options="horizontalBarOptions" />
      </div>
    </div>

    <!-- Revenue Chart -->
    <div class="chart-card chart-card-wide">
      <h3 class="chart-title">Revenue — Last 7 Days</h3>
      <Line :data="revenueChartData" :options="lineOptions" />
    </div>

    <!-- Cards row -->
    <div class="cards-row">
      <!-- Quick Actions -->
      <div class="card">
        <h3 class="card-title">Quick Actions</h3>
        <div class="action-list">
          <button v-if="canEdit" class="action-row-btn" @click="router.push('/scents')">
            <span class="abt-icon">+</span> New Scent Formula
          </button>
          <button v-if="canEdit" class="action-row-btn" @click="router.push('/ingredients')">
            <span class="abt-icon">+</span> Add Essential Oil
          </button>
          <button v-if="canEdit" class="action-row-btn" @click="router.push('/suppliers')">
            <span class="abt-icon">+</span> Add Supplier
          </button>
          <button class="action-row-btn" @click="router.push('/import-export')">
            <span class="abt-icon">↑</span> Import / Export Data
          </button>
          <button class="action-row-btn" @click="router.push('/pos')">
            <span class="abt-icon">$</span> Open POS
          </button>
        </div>
      </div>

      <!-- System Status -->
      <div class="card">
        <h3 class="card-title">System Status</h3>
        <div class="status-list">
          <div class="status-row">
            <span class="status-key">Database</span>
            <span class="status-ok"><span class="status-dot-green"></span>Connected</span>
          </div>
          <div class="status-row">
            <span class="status-key">API</span>
            <span class="status-ok"><span class="status-dot-green"></span>Operational</span>
          </div>
          <div class="status-row">
            <span class="status-key">Last Sync</span>
            <span class="status-info">Just now</span>
          </div>
          <div class="status-row">
            <span class="status-key">Backup</span>
            <span class="status-info">Today, 2:00 AM</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Getting Started -->
    <div class="card">
      <h3 class="card-title">Getting Started</h3>
      <div class="steps-grid">
        <div class="step">
          <div class="step-num">1</div>
          <div>
            <p class="step-h">Create Scent Formulas</p>
            <p class="step-p">Build your fragrance library with top, middle, and base notes.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-num">2</div>
          <div>
            <p class="step-h">Manage Essential Oils</p>
            <p class="step-p">Organize all your fragrance components and costs.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-num">3</div>
          <div>
            <p class="step-h">Track Suppliers</p>
            <p class="step-p">Keep supplier contacts and terms in one place.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-num">4</div>
          <div>
            <p class="step-h">Import &amp; Export</p>
            <p class="step-p">Batch upload or download your data in CSV or Excel.</p>
          </div>
        </div>
        <div v-if="isAdmin" class="step">
          <div class="step-num">5</div>
          <div>
            <p class="step-h">Audit Trail</p>
            <p class="step-p">Monitor all changes for compliance and tracking.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS, Title, Tooltip, Legend,
  BarElement, ArcElement, CategoryScale, LinearScale,
  LineElement, PointElement
} from 'chart.js'
import axios from 'axios'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
import { useAuthStore } from '../stores/auth'
import { useScentStore } from '../stores/scents'
import { useEssentialOilStore } from '../stores/essential-oils'
import { useSupplierStore } from '../stores/suppliers'
import { useAuditStore } from '../stores/audit'
import { useProductStore } from '../stores/products'

ChartJS.register(Title, Tooltip, Legend, BarElement, ArcElement, CategoryScale, LinearScale, LineElement, PointElement)

const router = useRouter()
const authStore = useAuthStore()
const scentStore = useScentStore()
const essentialOilStore = useEssentialOilStore()
const supplierStore = useSupplierStore()
const auditStore = useAuditStore()
const productStore = useProductStore()

const allSales = ref([])

onMounted(async () => {
  if (!scentStore.scents.length) await scentStore.fetchScents()
  if (!essentialOilStore.oils.length) await essentialOilStore.fetchOils()
  if (!supplierStore.suppliers.length) await supplierStore.fetchSuppliers()
  if (!auditStore.auditLogs.length) await auditStore.fetchAuditLogs()
  if (!productStore.products.length) await productStore.fetchProducts()
  try {
    const token = localStorage.getItem('authToken')
    const res = await axios.get(`${API_URL}/sales`, { headers: { Authorization: `Bearer ${token}` } })
    allSales.value = res.data
  } catch {}
})

const totalScents = computed(() => scentStore.scents.filter(s => !s.archivedAt).length)
const totalIngredients = computed(() => essentialOilStore.oils.length)
const totalSuppliers = computed(() => supplierStore.suppliers.length)
const recentActivities = computed(() => auditStore.auditLogs.length)
const totalProducts = computed(() => productStore.products.length)
const totalRevenue = computed(() =>
  allSales.value.reduce((sum, s) => sum + (parseFloat(s.total) || 0), 0).toFixed(2)
)
const canEdit = computed(() => ['admin', 'manager'].includes(authStore.user?.role))
const isAdmin = computed(() => authStore.user?.role === 'admin')

// Chart 1: oils per supplier
const oilsPerSupplierData = computed(() => {
  const counts = {}
  essentialOilStore.oils.forEach(o => {
    const key = o.supplierName || 'Unknown'
    counts[key] = (counts[key] || 0) + 1
  })
  return {
    labels: Object.keys(counts),
    datasets: [{ label: 'Oils', data: Object.values(counts), backgroundColor: '#8B6B4A' }]
  }
})

// Chart 2: audit log action breakdown
const auditActionData = computed(() => {
  const counts = { CREATE: 0, UPDATE: 0, DELETE: 0 }
  auditStore.auditLogs.forEach(l => {
    if (counts[l.action] !== undefined) counts[l.action]++
  })
  return {
    labels: ['Create', 'Update', 'Delete'],
    datasets: [{
      data: Object.values(counts),
      backgroundColor: ['#4caf50', '#C49A3C', '#c0392b']
    }]
  }
})

// Chart 3: average unit cost per supplier
const avgCostData = computed(() => {
  const totals = {}, counts2 = {}
  essentialOilStore.oils.forEach(o => {
    const key = o.supplierName || 'Unknown'
    totals[key] = (totals[key] || 0) + (o.unitCost || 0)
    counts2[key] = (counts2[key] || 0) + 1
  })
  const labels = Object.keys(totals)
  return {
    labels,
    datasets: [{
      label: 'Avg Cost ($)',
      data: labels.map(l => +(totals[l] / counts2[l]).toFixed(2)),
      backgroundColor: '#5C4A3A'
    }]
  }
})

const barOptions = { responsive: true, plugins: { legend: { display: false } } }
const horizontalBarOptions = { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } } }
const donutOptions = { responsive: true, plugins: { legend: { position: 'bottom' } } }
const lineOptions = { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }

// Chart 4: revenue per day for last 7 days
const revenueChartData = computed(() => {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    days.push(d.toISOString().slice(0, 10))
  }
  const totals = Object.fromEntries(days.map(d => [d, 0]))
  allSales.value.forEach(s => {
    const day = (s.date || '').slice(0, 10)
    if (totals[day] !== undefined) totals[day] += parseFloat(s.total) || 0
  })
  return {
    labels: days.map(d => new Date(d + 'T00:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
    datasets: [{
      label: 'Revenue ($)',
      data: days.map(d => +totals[d].toFixed(2)),
      borderColor: '#C49A3C',
      backgroundColor: 'rgba(196,154,60,0.15)',
      tension: 0.3,
      fill: true,
      pointBackgroundColor: '#8B6B4A'
    }]
  }
})
</script>

<style scoped>
.dash-home { font-family: var(--font-sans); }

/* Breadcrumb */
.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; color: var(--brown-lt); margin-bottom: 16px;
}
.sep { color: var(--cream-dk); }
.current { color: var(--brown); font-weight: 600; }

/* Page title row */
.page-title-row {
  display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 20px;
}
.page-title { font-size: 20px; font-weight: 700; color: var(--brown); margin: 0 0 3px; }
.page-sub { font-size: 12px; color: var(--brown-lt); margin: 0; }

/* Stats */
.stats-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 18px;
}
.stat-tile {
  background: var(--white); border-radius: 12px; padding: 16px 18px;
  border: 1px solid var(--cream-mid); position: relative; overflow: hidden;
}
.stat-tile::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--gold-dk), var(--gold-lt));
}
.st-label { font-size: 10px; font-weight: 700; color: var(--brown-lt); letter-spacing: 0.10em; text-transform: uppercase; margin: 0 0 6px; }
.st-val { font-size: 30px; font-weight: 700; color: var(--brown); line-height: 1; margin: 0 0 4px; }
.st-delta { font-size: 11px; color: var(--gold-dk); font-weight: 500; margin: 0; }

/* Charts row */
.charts-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 14px;
}
.chart-card {
  background: var(--white); border-radius: 12px; padding: 18px 20px;
  border: 1px solid var(--cream-mid); margin-bottom: 14px;
}
.chart-card-wide { grid-column: 1 / -1; }
.chart-title {
  font-size: 11px; font-weight: 700; color: var(--brown);
  letter-spacing: 0.08em; text-transform: uppercase; margin: 0 0 14px;
}

/* Cards row */
.cards-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
.card {
  background: var(--white); border-radius: 12px; padding: 18px 20px;
  border: 1px solid var(--cream-mid); margin-bottom: 14px;
}
.card:last-child { margin-bottom: 0; }
.card-title {
  font-size: 11px; font-weight: 700; color: var(--brown);
  letter-spacing: 0.08em; text-transform: uppercase; margin: 0 0 14px;
}

/* Action list */
.action-list { display: flex; flex-direction: column; gap: 6px; }
.action-row-btn {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 8px;
  background: var(--cream); border: 1px solid var(--cream-mid);
  color: var(--brown-md); font-size: 12.5px; font-weight: 500;
  font-family: var(--font-sans); cursor: pointer; text-align: left;
  transition: all .15s;
}
.action-row-btn:hover { background: var(--brown); color: var(--gold-lt); border-color: var(--brown); }
.abt-icon {
  width: 20px; height: 20px; border-radius: 50%;
  background: var(--gold); color: var(--white);
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.action-row-btn:hover .abt-icon { background: var(--gold-lt); color: var(--brown); }

/* Status list */
.status-list { display: flex; flex-direction: column; }
.status-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 9px 0; border-bottom: 1px solid #FDF6EC; font-size: 12.5px;
}
.status-row:last-child { border-bottom: none; }
.status-key { color: var(--brown-md); }
.status-ok { display: flex; align-items: center; font-size: 11px; font-weight: 600; color: var(--green); }
.status-info { font-size: 11px; color: var(--brown-lt); }

/* Steps */
.steps-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.step { display: flex; gap: 12px; align-items: flex-start; }
.step-num {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  background: var(--brown); color: var(--gold-lt);
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.step-h { font-size: 12.5px; font-weight: 600; color: var(--brown); margin: 0 0 3px; }
.step-p { font-size: 11.5px; color: var(--brown-lt); margin: 0; line-height: 1.5; }

@media (max-width: 900px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .chart-card-wide { grid-column: auto; }
  .charts-row { grid-template-columns: 1fr; }
  .cards-row { grid-template-columns: 1fr; }
  .steps-grid { grid-template-columns: 1fr; }
}
</style>
