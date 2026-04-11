import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginPage from '../views/LoginPage.vue'
import Dashboard from '../views/Dashboard.vue'
import DashboardHome from '../views/DashboardHome.vue'
import ScentLibrary from '../views/ScentLibrary.vue'
import EssentialOilsView from '../views/EssentialOilsView.vue'
import IngredientsView from '../views/IngredientsView.vue'
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
    path: '/',
    component: Dashboard,
    meta: { requiresAuth: true },
    children: [
      { path: 'dashboard',    name: 'Dashboard',    component: DashboardHome },
      { path: 'scents',       name: 'ScentLibrary', component: ScentLibrary },
      { path: 'oils',         name: 'EssentialOils', component: EssentialOilsView },
      { path: 'ingredients',  name: 'Ingredients',  component: IngredientsView },
      { path: 'suppliers',    name: 'Suppliers',    component: SuppliersView },
      { path: 'import-export', name: 'ImportExport', component: ImportExport },
      {
        path: 'audit-logs',
        name: 'AuditLogs',
        component: AuditLogs,
        meta: { requiresRole: ['admin', 'manager'] }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
  } else if (to.meta.requiresRole && !to.meta.requiresRole.includes(authStore.user?.role)) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
