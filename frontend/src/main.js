import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Login from './views/Login.vue'
import CompetitionView from './views/CompetitionView.vue'
import TrainingView from './views/TrainingView.vue'
import ResultView from './views/ResultView.vue'
import TaskSubmitView from './views/TaskSubmitView.vue'
import EvaluationView from './views/EvaluationView.vue'
import AdminView from './views/AdminView.vue'
import LeaderboardView from './views/LeaderboardView.vue'

const routes = [
  { path: '/login', component: Login },
  { path: '/', redirect: '/login' },
  { path: '/competition', component: CompetitionView, meta: { requiresAuth: true, role: 'user' } },
  { path: '/training', component: TrainingView, meta: { requiresAuth: true, role: 'user' } },
  { path: '/result', component: ResultView, meta: { requiresAuth: true, role: 'user' } },
  { path: '/task-submit', component: TaskSubmitView, meta: { requiresAuth: true, role: 'user' } },
  { path: '/evaluation', component: EvaluationView, meta: { requiresAuth: true, role: 'user' } },
  { path: '/admin', component: AdminView, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/leaderboard', component: LeaderboardView, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查登录状态和角色
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  const userRole = user?.role || 'user'
  
  if (to.meta.requiresAuth && !token) {
    // 需要登录但未登录，跳转到登录页
    next('/login')
  } else if (to.path === '/login' && token) {
    // 已登录访问登录页，根据角色跳转
    if (userRole === 'admin') {
      next('/admin')
    } else {
      next('/competition')
    }
  } else if (to.meta.requiresAuth && to.meta.role && to.meta.role !== userRole) {
    // 角色不匹配，跳转到对应角色的首页
    if (userRole === 'admin') {
      next('/admin')
    } else {
      next('/competition')
    }
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
