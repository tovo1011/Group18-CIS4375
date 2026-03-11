<template>
  <div class="dashboard">
    <nav class="navbar">
      <div class="navbar-content">
        <h1 class="navbar-title">🌹 Perfume Store Dashboard</h1>
        <div class="navbar-user">
          <span>Welcome, {{ authStore.user?.name }}</span>
          <button @click="handleLogout" class="logout-btn">Logout</button>
        </div>
      </div>
    </nav>

    <div class="dashboard-content">
      <aside class="sidebar">
        <ul class="menu">
          <li class="menu-item active">
            <span class="menu-icon">📊</span>
            <span>Dashboard</span>
          </li>
          <li class="menu-item">
            <span class="menu-icon">🛍️</span>
            <span>Products</span>
          </li>
          <li class="menu-item">
            <span class="menu-icon">👥</span>
            <span>Customers</span>
          </li>
          <li class="menu-item">
            <span class="menu-icon">📈</span>
            <span>Analytics</span>
          </li>
          <li class="menu-item">
            <span class="menu-icon">⚙️</span>
            <span>Settings</span>
          </li>
        </ul>
      </aside>

      <main class="main-content">
        <div class="welcome-section">
          <h2>Welcome to Your Perfume Store Dashboard</h2>
          <p>Manage your perfume inventory, customers, and sales in one place.</p>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📦</div>
            <div class="stat-info">
              <h3>Total Products</h3>
              <p class="stat-value">1,248</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">💵</div>
            <div class="stat-info">
              <h3>Total Revenue</h3>
              <p class="stat-value">$45,230</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-info">
              <h3>Total Customers</h3>
              <p class="stat-value">3,542</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
              <h3>Monthly Orders</h3>
              <p class="stat-value">892</p>
            </div>
          </div>
        </div>

        <div class="content-cards">
          <div class="card">
            <h3>Popular Perfumes</h3>
            <ul class="product-list">
              <li>
                <span class="product-name">Chanel No.5</span>
                <span class="product-sales">2,450 sold</span>
              </li>
              <li>
                <span class="product-name">Dior Sauvage</span>
                <span class="product-sales">2,180 sold</span>
              </li>
              <li>
                <span class="product-name">Guerlain L'Homme Ideal</span>
                <span class="product-sales">1,920 sold</span>
              </li>
              <li>
                <span class="product-name">Yves Saint Laurent Black Opium</span>
                <span class="product-sales">1,680 sold</span>
              </li>
            </ul>
          </div>

          <div class="card">
            <h3>Recent Orders</h3>
            <ul class="order-list">
              <li>
                <span class="order-id">Order #10234</span>
                <span class="order-price">$125.99</span>
              </li>
              <li>
                <span class="order-id">Order #10233</span>
                <span class="order-price">$89.50</span>
              </li>
              <li>
                <span class="order-id">Order #10232</span>
                <span class="order-price">$245.00</span>
              </li>
              <li>
                <span class="order-id">Order #10231</span>
                <span class="order-price">$67.25</span>
              </li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

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
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #f3de22 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  max-width: 100%;
}

.navbar-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logout-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.dashboard-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #ddd;
  overflow-y: auto;
}

.menu {
  list-style: none;
  padding: 20px 0;
  margin: 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 20px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: #f5f5f5;
  color: #667eea;
}

.menu-item.active {
  background: #f0f7ff;
  color: #667eea;
  border-left-color: #667eea;
}

.menu-icon {
  font-size: 18px;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
}

.welcome-section {
  margin-bottom: 40px;
}

.welcome-section h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 28px;
}

.welcome-section p {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 15px;
  align-items: center;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 32px;
}

.stat-info h3 {
  margin: 0 0 5px 0;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.stat-value {
  margin: 0;
  color: #667eea;
  font-size: 24px;
  font-weight: 600;
}

.content-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
}

.product-list,
.order-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.product-list li,
.order-list li {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}

.product-list li:last-child,
.order-list li:last-child {
  border-bottom: none;
}

.product-name,
.order-id {
  color: #333;
  font-weight: 500;
}

.product-sales,
.order-price {
  color: #667eea;
  font-weight: 600;
}

@media (max-width: 768px) {
  .dashboard-content {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #ddd;
  }

  .menu {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    padding: 10px 0;
  }

  .menu-item {
    flex-shrink: 0;
    padding: 10px 15px;
    border-left: none;
    border-bottom: 3px solid transparent;
  }

  .menu-item.active {
    border-left: none;
    border-bottom-color: #667eea;
  }

  .navbar-content {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .content-cards {
    grid-template-columns: 1fr;
  }
}
</style>
