import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import CompetitionView from './views/CompetitionView.vue'
import TrainingView from './views/TrainingView.vue'
import MonitorView from './views/MonitorView.vue'
import ResultView from './views/ResultView.vue'
import TaskSubmitView from './views/TaskSubmitView.vue'
import EvaluationView from './views/EvaluationView.vue'

const routes = [
  { path: '/', redirect: '/competition' },
  { path: '/competition', component: CompetitionView },
  { path: '/training', component: TrainingView },
  { path: '/monitor', component: MonitorView },
  { path: '/result', component: ResultView },
  { path: '/task-submit', component: TaskSubmitView },
  { path: '/evaluation', component: EvaluationView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
