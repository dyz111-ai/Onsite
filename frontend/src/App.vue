<template>
  <div id="app">
    <!-- 只在非登录页和非管理员页显示侧边栏 -->
    <nav v-if="!isLoginPage && !isAdminPage" class="sidebar">
      <div class="logo">Onsite测训一体</div>
      <ul class="nav-menu">
        <li>
          <router-link to="/competition" class="nav-item">赛题查看</router-link>
        </li>
        <li>
          <router-link to="/task-submit" class="nav-item">场景提交</router-link>
        </li>
        <li>
          <router-link to="/training" class="nav-item">训练提交</router-link>
        </li>
        <li>
          <router-link to="/evaluation" class="nav-item">测试评估</router-link>
        </li>
        <li>
          <router-link to="/result" class="nav-item">结果展示</router-link>
        </li>
        <li>
          <router-link to="/leaderboard" class="nav-item">排行榜</router-link>
        </li>
      </ul>
      <div class="user-info">
        <div class="username">{{ username }}</div>
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </div>
    </nav>
    <main :class="(isLoginPage || isAdminPage) ? 'main-content-full' : 'main-content'">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCurrentUser, logout } from './utils/auth'

const route = useRoute()
const router = useRouter()

const isLoginPage = computed(() => route.path === '/login')
const isAdminPage = computed(() => route.path === '/admin')
const username = ref(getCurrentUser()?.username || getCurrentUser()?.account || '未登录')

// 监听路由变化，更新用户名
watch(() => route.path, () => {
  const user = getCurrentUser()
  username.value = user?.username || user?.account || '未登录'
})

const handleLogout = () => {
  logout()
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: Arial, sans-serif;
  min-height: 100vh;
}

#app:not(:has(.auth-container)) {
  display: flex;
  background: #f5f5f5;
}

.sidebar {
  width: 200px;
  background: #2c3e50;
  color: white;
  min-height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
}

.logo {
  padding: 2rem 1rem;
  font-size: 1.2rem;
  font-weight: bold;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-menu {
  list-style: none;
  padding: 1rem 0;
}

.nav-menu li {
  margin: 0;
}

.nav-item {
  display: block;
  padding: 1rem 1.5rem;
  color: #ecf0f1;
  text-decoration: none;
  transition: background 0.3s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.router-link-active {
  background: #42b983;
  border-left: 4px solid #fff;
}

.main-content {
  margin-left: 200px;
  padding: 0;
  flex: 1;
  min-height: 100vh;
  width: calc(100% - 200px);
  max-width: 100%;
  box-sizing: border-box;
}

.main-content-full {
  margin-left: 0;
  padding: 0;
  flex: 1;
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.user-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.username {
  color: #ecf0f1;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  text-align: center;
}

.logout-btn {
  width: 100%;
  padding: 0.5rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: #c0392b;
}
</style>
