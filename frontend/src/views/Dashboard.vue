<template>
  <div class="dashboard">
    <nav class="navbar">
      <div class="navbar-content">
        <h1 class="navbar-title">🌹 T4Scents</h1>
        <div class="navbar-user">
          <span>Welcome, {{ authStore.user?.name }}</span>
          <button @click="handleLogout" class="logout-btn">Logout</button>
        </div>
      </div>
    </nav>

    <div class="dashboard-container">
      <aside class="sidebar">
        <ul class="menu">
          <li
            v-for="item in menuItems"
            :key="item.name"
            :class="['menu-item', { active: isActive(item.route) }]"
            @click="navigateTo(item.route)"
          >
            <span class="menu-icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </li>
        </ul>
        <div class="role-badge">
          <span :class="`badge-${authStore.user?.role}`">
            {{ authStore.user?.role?.toUpperCase() }}
          </span>
        </div>
      </aside>

      <main class="main-content">
        <div class="welcome-section">
          <h2>Welcome to T4Scents Dashboard</h2>
          <p>Manage your fragrance formulas, ingredients, suppliers, and inventory in one centralized platform.</p>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">🌹</div>
            <div class="stat-info">
              <h3>Total Scents</h3>
              <p class="stat-value">{{ totalScents }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">🧪</div>
            <div class="stat-info">
              <h3>Total Ingredients</h3>
              <p class="stat-value">{{ totalIngredients }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">🏢</div>
            <div class="stat-info">
              <h3>Active Suppliers</h3>
              <p class="stat-value">{{ totalSuppliers }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-info">
              <h3>Recent Activities</h3>
              <p class="stat-value">{{ recentActivities }}</p>
            </div>
          </div>
        </div>

        <div class="content-cards">
          <div class="card">
            <h3>Quick Actions</h3>
            <div class="quick-actions">
              <button v-if="canEdit" class="action-btn" @click="navigateTo('/scents')">
                + New Scent
              </button>
              <button v-if="canEdit" class="action-btn" @click="navigateTo('/ingredients')">
                + Add Ingredient
              </button>
              <button v-if="canEdit" class="action-btn" @click="navigateTo('/suppliers')">
                + Add Supplier
              </button>
              <button class="action-btn" @click="navigateTo('/import-export')">
                📤 Import/Export
              </button>
            </div>
          </div>

          <div class="card">
            <h3>System Status</h3>
            <div class="status-list">
              <div class="status-item">
                <span class="status-label">Database Connection</span>
                <span class="status-indicator success">● Connected</span>
              </div>
              <div class="status-item">
                <span class="status-label">API Status</span>
                <span class="status-indicator success">● Operational</span>
              </div>
              <div class="status-item">
                <span class="status-label">Last Sync</span>
                <span class="status-value">Just now</span>
              </div>
              <div class="status-item">
                <span class="status-label">Data Backup</span>
                <span class="status-value">Today at 2:00 AM</span>
              </div>
            </div>
          </div>
        </div>

        <div class="info-section">
          <h3>📋 Getting Started</h3>
          <div class="getting-started">
            <div class="step">
              <span class="step-number">1</span>
              <div class="step-content">
                <h4>Create Scent Formulas</h4>
                <p>Go to <router-link to="/scents">Scent Library</router-link> to create new fragrance formulas with top, middle, and base notes.</p>
              </div>
            </div>
            <div class="step">
              <span class="step-number">2</span>
              <div class="step-content">
                <h4>Manage Ingredients</h4>
                <p>Visit <router-link to="/ingredients">Ingredients</router-link> to add and organize all your fragrance components.</p>
              </div>
            </div>
            <div class="step">
              <span class="step-number">3</span>
              <div class="step-content">
                <h4>Track Suppliers</h4>
                <p>Maintain supplier information in <router-link to="/suppliers">Suppliers</router-link> for better inventory management.</p>
              </div>
            </div>
            <div class="step">
              <span class="step-number">4</span>
              <div class="step-content">
                <h4>Import & Export</h4>
                <p>Use <router-link to="/import-export">Import/Export</router-link> to batch upload or download your data.</p>
              </div>
            </div>
            <div v-if="isAdmin" class="step">
              <span class="step-number">5</span>
              <div class="step-content">
                <h4>Audit Trail</h4>
                <p>Monitor all changes in <router-link to="/audit-logs">Audit Logs</router-link> for compliance and tracking.</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useScentStore } from '../stores/scents'
import { useIngredientStore } from '../stores/ingredients'
import { useSupplierStore } from '../stores/suppliers'
import { useAuditStore } from '../stores/audit'

const router = useRouter()
const authStore = useAuthStore()
const scentStore = useScentStore()
const ingredientStore = useIngredientStore()
const supplierStore = useSupplierStore()
const auditStore = useAuditStore()

const currentRoute = ref('dashboard')

const menuItems = computed(() => {
  const items = [
    { name: 'dashboard', label: 'Dashboard', icon: '📊', route: '/dashboard' },
    { name: 'scents', label: 'Scent Library', icon: '🌹', route: '/scents' },
    { name: 'ingredients', label: 'Ingredients', icon: '🧪', route: '/ingredients' },
    { name: 'suppliers', label: 'Suppliers', icon: '🏢', route: '/suppliers' },
    { name: 'import-export', label: 'Import/Export', icon: '📤', route: '/import-export' }
  ]

  if (['admin', 'manager'].includes(authStore.user?.role)) {
    items.push({ name: 'audit', label: 'Audit Logs', icon: '📋', route: '/audit-logs' })
  }

  return items
})

const totalScents = computed(() => scentStore.scents.filter(s => !s.archivedAt).length)
const totalIngredients = computed(() => ingredientStore.ingredients.length)
const totalSuppliers = computed(() => supplierStore.suppliers.length)
const recentActivities = computed(() => auditStore.auditLogs.length)

const canEdit = computed(() => {
  return ['admin', 'manager'].includes(authStore.user?.role)
})

const isAdmin = computed(() => {
  return authStore.user?.role === 'admin'
})

const isActive = (route) => {
  return router.currentRoute.value.path === route
}

const navigateTo = (route) => {
  router.push(route)
  currentRoute.value = route
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  max-width: 100%;
}

.navbar-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 16px;
}

.navbar-user span {
  font-size: 14px;
}

.logout-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.dashboard-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 260px;
  background: white;
  border-right: 1px solid #ddd;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.menu {
  list-style: none;
  margin: 0;
  padding: 16px 0;
  flex: 1;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #666;
  font-size: 14px;
}

.menu-item:hover {
  background: #f5f5f5;
  color: #667eea;
}

.menu-item.active {
  background: #f0f3ff;
  color: #667eea;
  border-right: 3px solid #667eea;
  font-weight: 600;
}

.menu-icon {
  font-size: 18px;
}

.role-badge {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  text-align: center;
}

.badge-admin {
  display: inline-block;
  background: #dc3545;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}

.badge-manager {
  display: inline-block;
  background: #ffc107;
  color: #333;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}

.badge-viewer {
  display: inline-block;
  background: #6c757d;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
}

.welcome-section {
  margin-bottom: 30px;
}

.welcome-section h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #333;
}

.welcome-section p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 16px;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  text-align: center;
  min-width: 50px;
}

.stat-info h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
  font-weight: 600;
}

.stat-value {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.content-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #333;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  padding: 10px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;
  text-align: left;
}

.action-btn:hover {
  background: #5568d3;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  font-size: 13px;
  color: #666;
}

.status-indicator {
  font-size: 13px;
  font-weight: 600;
}

.status-indicator.success {
  color: #27ae60;
}

.status-value {
  font-size: 13px;
  color: #999;
}

.info-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #333;
}

.getting-started {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step {
  display: flex;
  gap: 16px;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #333;
}

.step-content p {
  margin: 0;
  font-size: 13px;
  color: #666;
}

.step-content a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.step-content a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .dashboard-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #ddd;
  }

  .menu {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    padding: 8px;
    gap: 4px;
  }

  .menu-item {
    justify-content: center;
    padding: 8px;
    flex-direction: column;
    text-align: center;
  }

  .menu-item.active {
    border-right: none;
    border-bottom: 3px solid #667eea;
  }

  .main-content {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-card {
    flex-direction: column;
  }

  .content-cards {
    grid-template-columns: 1fr;
  }
}
</style>
