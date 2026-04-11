<template>
  <div class="dashboard">
    <!-- ── Topbar ── -->
    <nav class="topbar">
      <div class="topbar-left">
        <img :src="'/logo.png'" alt="T4 Scents" class="nav-logo-img" />
        <span class="nav-sep"></span>
      </div>
      <div class="topbar-right">
        <span class="nav-welcome">Welcome, <strong>{{ authStore.user?.name }}</strong></span>
        <span :class="`role-tag role-${authStore.user?.role}`">{{ authStore.user?.role?.toUpperCase() }}</span>
        <button @click="handleLogout" class="signout-btn">Sign Out</button>
      </div>
    </nav>

    <div class="layout">
      <!-- ── Sidebar ── -->
      <aside class="sidebar">
        <div class="sidebar-section">
          <p class="sidebar-label">Main</p>
          <ul class="nav-menu">
            <li
              v-for="item in menuItems"
              :key="item.name"
              :class="['nav-link', { active: isActive(item.route) }]"
              @click="navigateTo(item.route)"
            >
              <span class="nav-dot"></span>
              {{ item.label }}
            </li>
          </ul>
        </div>

        <div class="sidebar-footer">
          <div class="user-card">
            <div class="user-avatar">{{ authStore.user?.name?.charAt(0)?.toUpperCase() || 'U' }}</div>
            <div class="user-info">
              <div class="user-name">{{ authStore.user?.name }}</div>
              <div class="user-email">{{ authStore.user?.email }}</div>
            </div>
          </div>
        </div>
      </aside>

      <!-- ── Main content (router view renders here) ── -->
      <main class="main-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, RouterView } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const menuItems = computed(() => {
  const items = [
    { name: 'dashboard',     label: 'Dashboard',      route: '/dashboard' },
    { name: 'scents',        label: 'Scent Library',   route: '/scents' },
    { name: 'oils',          label: 'Essential Oils',  route: '/oils' },
    { name: 'ingredients',   label: 'Ingredients',     route: '/ingredients' },
    { name: 'suppliers',     label: 'Suppliers',       route: '/suppliers' },
    { name: 'import-export', label: 'Import / Export', route: '/import-export' },
  ]
  if (['admin', 'manager'].includes(authStore.user?.role)) {
    items.push({ name: 'audit', label: 'Audit Logs', route: '/audit-logs' })
  }
  return items
})

const isActive = (route) => router.currentRoute.value.path === route

const navigateTo = (route) => router.push(route)

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
  background: var(--cream);
}

/* ── Topbar ── */
.topbar {
  height: 56px;
  background: var(--brown);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
  border-bottom: 2px solid var(--gold-dk);
  box-shadow: 0 2px 16px rgba(44,24,16,0.4);
  z-index: 100;
}

.topbar-left { display: flex; align-items: center; gap: 12px; }

.nav-logo-img {
  height: 36px;
  width: auto;
  display: block;
  /* invert dark bg so logo gold shows properly */
  filter: brightness(1.1) contrast(1.05);
}

.nav-sep { width: 1px; height: 18px; background: rgba(201,160,72,0.25); }
.nav-sub { font-size: 10px; color: rgba(232,201,123,0.6); letter-spacing: 0.18em; text-transform: uppercase; font-weight: 500; }

.topbar-right { display: flex; align-items: center; gap: 10px; }
.nav-welcome { font-size: 12px; color: rgba(249,240,225,0.75); }
.nav-welcome strong { color: var(--gold-lt); }

.role-tag {
  font-size: 9px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
  padding: 3px 9px; border-radius: 4px;
  background: rgba(201,160,72,0.18); color: var(--gold);
  border: 1px solid rgba(201,160,72,0.3);
}

.signout-btn {
  padding: 6px 14px;
  background: transparent;
  border: 1px solid rgba(201,160,72,0.3);
  border-radius: 6px;
  color: var(--gold-lt);
  font-size: 11px; font-weight: 600;
  font-family: var(--font-sans);
  cursor: pointer; letter-spacing: 0.04em;
  transition: all .18s;
}
.signout-btn:hover { background: rgba(201,160,72,0.12); border-color: var(--gold); }

/* ── Layout ── */
.layout { display: flex; flex: 1; overflow: hidden; }

/* ── Sidebar ── */
.sidebar {
  width: 220px;
  background: var(--white);
  border-right: 1px solid var(--cream-mid);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-section { padding: 20px 14px 8px; }
.sidebar-label {
  font-size: 9px; font-weight: 700; color: var(--brown-lt);
  letter-spacing: 0.20em; text-transform: uppercase;
  margin: 0 0 6px; padding-left: 8px;
}

.nav-menu { list-style: none; margin: 0; padding: 0; }

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  font-size: 12.5px; font-weight: 500;
  color: var(--brown-lt);
  cursor: pointer;
  transition: all .15s;
  margin-bottom: 1px;
}
.nav-link:hover { background: var(--cream); color: var(--brown-md); }
.nav-link.active { background: var(--brown); color: var(--gold-lt); font-weight: 600; }

.nav-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: currentColor; opacity: 0.5; flex-shrink: 0;
}
.nav-link.active .nav-dot { background: var(--gold); opacity: 1; }

/* ── Sidebar footer ── */
.sidebar-footer { margin-top: auto; padding: 14px; border-top: 1px solid var(--cream-mid); }
.user-card {
  display: flex; align-items: center; gap: 10px;
  background: var(--cream); border-radius: 10px;
  padding: 10px 12px; border: 1px solid var(--cream-mid);
}
.user-avatar {
  width: 30px; height: 30px; border-radius: 8px;
  background: var(--brown); color: var(--gold-lt);
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.user-name { font-size: 12px; font-weight: 600; color: var(--brown); }
.user-email { font-size: 10px; color: var(--brown-lt); margin-top: 1px; }

/* ── Main ── */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .layout { flex-direction: column; }
  .sidebar { width: 100%; border-right: none; border-bottom: 1px solid var(--cream-mid); }
  .nav-menu { display: flex; flex-wrap: wrap; gap: 4px; }
  .nav-link { padding: 7px 10px; font-size: 12px; }
  .sidebar-footer { display: none; }
  .main-content { padding: 16px; }
}
</style>
