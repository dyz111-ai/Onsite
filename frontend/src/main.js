import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Login from './views/Login.vue'
import CompetitionView from './views/CompetitionView.vue'
import CompetitionManagementView from './views/CompetitionManagementView.vue'
import TrainingView from './views/TrainingView.vue'
import ResultView from './views/ResultView.vue'
import TaskSubmitView from './views/TaskSubmitView.vue'
import EvaluationView from './views/EvaluationView.vue'

const routes = [
  { path: '/login', component: Login },
  { path: '/', redirect: '/login' },
  { path: '/competition', component: CompetitionView, meta: { requiresAuth: true } },
  { path: '/competition-management', component: CompetitionManagementView, meta: { requiresAuth: true } },
  { path: '/training', component: TrainingView, meta: { requiresAuth: true } },
  { path: '/result', component: ResultView, meta: { requiresAuth: true } },
  { path: '/task-submit', component: TaskSubmitView, meta: { requiresAuth: true } },
  { path: '/evaluation', component: EvaluationView, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    // 需要登录但未登录，跳转到登录页
    next('/login')
  } else if (to.path === '/login' && token) {
    // 已登录访问登录页，跳转到比赛页面
    next('/competition')
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
