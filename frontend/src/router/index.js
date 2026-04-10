import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginPage from '../views/LoginPage.vue'
import Dashboard from '../views/Dashboard.vue'
import ScentLibrary from '../views/ScentLibrary.vue'
import EssentialOilsView from '../views/EssentialOilsView.vue'
import SuppliersView from '../views/SuppliersView.vue'
import AuditLogs from '../views/AuditLogs.vue'
import ImportExport from '../views/ImportExport.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/scents',
    name: 'ScentLibrary',
    component: ScentLibrary,
    meta: { requiresAuth: true }
  },
  {
    path: '/oils',
    name: 'EssentialOils',
    component: EssentialOilsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/suppliers',
    name: 'Suppliers',
    component: SuppliersView,
    meta: { requiresAuth: true }
  },
  {
    path: '/audit-logs',
    name: 'AuditLogs',
    component: AuditLogs,
    meta: { requiresAuth: true, requiresRole: ['admin', 'manager'] }
  },
  {
    path: '/import-export',
    name: 'ImportExport',
    component: ImportExport,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for authentication and authorization
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
  } else if (to.meta.requiresRole && !to.meta.requiresRole.includes(authStore.user?.role)) {
    // Redirect to dashboard if user doesn't have required role
    next('/dashboard')
  } else {
    next()
  }
})

export default router
