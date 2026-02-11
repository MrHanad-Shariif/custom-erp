import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { left: 0, top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue'),
      meta: { title: 'Dashboard', requiresAuth: true },
    },
    // CRM
    {
      path: '/crm/leads',
      name: 'Leads',
      component: () => import('../views/ERP/CrmLeads.vue'),
      meta: { title: 'Leads', requiresAuth: true, permission: 'crm.view' },
    },
    {
      path: '/crm/customers',
      name: 'Customers',
      component: () => import('../views/ERP/CrmCustomers.vue'),
      meta: { title: 'Customers', requiresAuth: true, permission: 'crm.view' },
    },
    {
      path: '/crm/customers/:id',
      name: 'Customer360',
      component: () => import('../views/ERP/Customer360.vue'),
      meta: { title: 'Customer 360', requiresAuth: true, permission: 'crm.view' },
    },
    // HRM
    {
      path: '/hrm/employees',
      name: 'Employees',
      component: () => import('../views/ERP/HrmEmployees.vue'),
      meta: { title: 'Employees', requiresAuth: true, permission: 'hrm.view' },
    },
    {
      path: '/hrm/payroll',
      name: 'Payroll',
      component: () => import('../views/ERP/HrmPayroll.vue'),
      meta: { title: 'Payroll', requiresAuth: true, permission: 'hrm.view' },
    },
    // Inventory
    {
      path: '/inventory/warehouses',
      name: 'Warehouses',
      component: () => import('../views/ERP/InventoryWarehouses.vue'),
      meta: { title: 'Warehouses', requiresAuth: true, permission: 'inventory.view' },
    },
    {
      path: '/inventory/skus',
      name: 'SKUs',
      component: () => import('../views/ERP/InventorySkus.vue'),
      meta: { title: 'SKUs', requiresAuth: true, permission: 'inventory.view' },
    },
    {
      path: '/inventory/stock',
      name: 'Stock',
      component: () => import('../views/ERP/InventoryStock.vue'),
      meta: { title: 'Stock', requiresAuth: true, permission: 'inventory.view' },
    },
    {
      path: '/inventory/purchase-orders',
      name: 'PurchaseOrders',
      component: () => import('../views/ERP/InventoryPurchaseOrders.vue'),
      meta: { title: 'Purchase Orders', requiresAuth: true, permission: 'inventory.view' },
    },
    // Project Management
    {
      path: '/pm/projects',
      name: 'Projects',
      component: () => import('../views/ERP/PmProjects.vue'),
      meta: { title: 'Projects', requiresAuth: true, permission: 'pm.view' },
    },
    {
      path: '/pm/projects/:id',
      name: 'ProjectDetail',
      component: () => import('../views/ERP/PmProjectDetail.vue'),
      meta: { title: 'Project', requiresAuth: true, permission: 'pm.view' },
    },
    {
      path: '/pm/timesheets',
      name: 'Timesheets',
      component: () => import('../views/ERP/PmTimesheets.vue'),
      meta: { title: 'Timesheets', requiresAuth: true, permission: 'pm.view' },
    },
    // Finance
    {
      path: '/finance/invoices',
      name: 'Invoices',
      component: () => import('../views/ERP/FinanceInvoices.vue'),
      meta: { title: 'Invoices', requiresAuth: true, permission: 'finance.view' },
    },
    // Authentication (users & roles)
    {
      path: '/auth/users',
      name: 'AuthUsers',
      component: () => import('../views/Auth/AuthUsers.vue'),
      meta: { title: 'Users', requiresAuth: true, permission: 'auth.view' },
    },
    {
      path: '/auth/roles',
      name: 'AuthRoles',
      component: () => import('../views/Auth/AuthRoles.vue'),
      meta: { title: 'Roles', requiresAuth: true, permission: 'auth.view' },
    },
    // Auth (public)
    {
      path: '/signin',
      name: 'Signin',
      component: () => import('../views/Auth/Signin.vue'),
      meta: { title: 'Sign In' },
    },
    {
      path: '/signup',
      name: 'Signup',
      component: () => import('../views/Auth/Signup.vue'),
      meta: { title: 'Sign Up' },
    },
    {
      path: '/signin/callback',
      name: 'SigninCallback',
      component: () => import('../views/Auth/SigninCallback.vue'),
      meta: { title: 'Sign In' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/Errors/FourZeroFour.vue'),
      meta: { title: '404' },
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title ? `${String(to.meta.title)} | Custom ERP` : 'Custom ERP'

  const publicPaths = ['/signin', '/signup', '/signin/callback']
  const isPublic = publicPaths.some((p) => to.path === p)

  const token = localStorage.getItem('erp_access_token')
  if (!token && to.meta.requiresAuth) {
    next({ path: '/signin', query: { redirect: to.fullPath } })
    return
  }
  if (token && isPublic) {
    next({ path: (to.query.redirect as string) || '/' })
    return
  }
  next()
})

export default router
