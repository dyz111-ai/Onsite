<template>
  <div id="app">
    <!-- 修改：允许管理员页面显示侧边栏 -->
    <nav v-if="!isLoginPage" class="sidebar"> <!-- 移除了 !isAdminPage 条件 -->
      <div class="logo">Onsite测训一体</div>
      <ul class="nav-menu">
        <li>
          <router-link to="/competition" class="nav-item">赛题查看</router-link>
        </li>
        <li v-if="!isAdmin">
          <router-link to="/task-submit" class="nav-item">场景提交</router-link>
        </li>
        <li v-if="!isAdmin">
          <router-link to="/training" class="nav-item">训练提交</router-link>
        </li>
        <li v-if="!isAdmin">
          <router-link to="/evaluation" class="nav-item">测试评估</router-link>
        </li>
        <li>
          <router-link to="/leaderboard" class="nav-item">排行榜</router-link>
        </li>
        <!-- 添加管理员页面链接 -->
        <li v-if="isAdmin">
          <router-link to="/admin" class="nav-item">管理员</router-link>
        </li>
      </ul>
      <div class="user-info">
        <div class="username">{{ username }}</div>
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </div>
    </nav>
    <main :class="(isLoginPage) ? 'main-content-full' : 'main-content'">
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
const isAdmin = ref(false) // 添加管理员权限判断

// 监听路由变化，更新用户名和权限
watch(() => route.path, () => {
  const user = getCurrentUser()
  username.value = user?.username || user?.account || '未登录'
  // 根据用户角色判断是否为管理员
  isAdmin.value = user?.role === 'admin' || false
})

const handleLogout = () => {
  logout()
  // 如果当前是管理员页面，登出后跳转到登录页
  if (isAdminPage.value) {
    router.push('/login')
  }
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
  width: 100%;
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
  width: 100%;
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
