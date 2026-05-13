import { createRouter, createWebHistory } from 'vue-router'
import PublicLayout from '../layouts/PublicLayout.vue'
import UserLayout from '../layouts/UserLayout.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import LibrarianLayout from '../layouts/LibrarianLayout.vue'
import { useAuthStore } from '../stores/authStore'

const routes = [
  {
    path: '',
    component: PublicLayout,
    children: [
      { path: 'login', name: 'login', component: () => import('../views/auth/LoginView.vue') },
      { path: 'register', name: 'register', component: () => import('../views/auth/RegisterView.vue') },
      { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
      { path: 'catalog', name: 'catalog', component: () => import('../views/CatalogView.vue') },
      { path: 'book/:id', name: 'book-detail', component: () => import('../views/BookDetailView.vue') }
    ]
  },
  {
    path: '/cabinet',
    component: UserLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: () => import('../views/reader/DashboardView.vue') },
      { path: 'catalog', name: 'reader-catalog', component: () => import('../views/CatalogView.vue') },
      { path: 'book/:id', name: 'reader-book-detail', component: () => import('../views/BookDetailView.vue') },
      { path: 'loans', name: 'my-loans', component: () => import('../views/reader/MyLoansView.vue') },
      { path: 'reservations', name: 'my-reservations', component: () => import('../views/reader/MyReservationsView.vue') }
    ]
  },
  {
    path: '/librarian',
    component: LibrarianLayout,
    meta: { requiresAuth: true, roles: ['librarian', 'admin'] },
    children: [
      { path: '', name: 'librarian-dashboard', component: () => import('../views/librarian/LibrarianDashboard.vue') },
      { path: 'checkout', name: 'checkout', component: () => import('../views/librarian/CheckoutView.vue') },
      { path: 'inventory', name: 'inventory', component: () => import('../views/librarian/InventoryView.vue') },
      { path: 'loans', name: 'loans', component: () => import('../views/librarian/LoansView.vue') },
      { path: 'reservations', name: 'reservations-queue', component: () => import('../views/librarian/ReservationsView.vue') },
      { path: 'fines', name: 'fines', component: () => import('../views/librarian/FinesView.vue') },
      { path: 'reports', name: 'reports', component: () => import('../views/librarian/ReportsView.vue') }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      { path: '', name: 'admin-dashboard', component: () => import('../views/admin/AdminDashboard.vue') },
      { path: 'users', name: 'admin-users', component: () => import('../views/admin/UsersView.vue') },
      { path: 'settings', name: 'admin-settings', component: () => import('../views/admin/SettingsView.vue') },
      { path: 'genres', name: 'admin-genres', component: () => import('../views/admin/GenresView.vue') },
      { path: 'audit', name: 'admin-audit', component: () => import('../views/admin/AuditView.vue') }
    ]
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('../views/NotFound.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (auth.token && !auth.user && !auth.loading) {
    await auth.init()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.meta.roles && !to.meta.roles.includes(auth.user?.role)) {
    // Редирект на главную страницу по роли, если доступ запрещён
    if (auth.user?.role === 'admin') next('/admin')
    else if (auth.user?.role === 'librarian') next('/librarian')
    else next('/cabinet')
  } else {
    next()
  }
})

export default router