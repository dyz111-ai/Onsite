<template>
  <div class="admin-container">
    <div class="admin-header">
      <h1>管理员页面</h1>
      <div class="admin-user-info">
        <span class="admin-name">{{ adminName }}</span>
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </div>
    </div>
    <div class="admin-content">
      <p>管理员功能开发中...</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { logout } from '../utils/auth'

export default {
  name: 'AdminView',
  setup() {
    const router = useRouter()
    const adminName = ref('')

    onMounted(() => {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        const user = JSON.parse(userStr)
        adminName.value = user.account || '管理员'
      }
    })

    const handleLogout = () => {
      logout()
      router.push('/login')
    }

    return {
      adminName,
      handleLogout
    }
  }
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.admin-header {
  background: white;
  padding: 20px 40px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h1 {
  color: #333;
  margin: 0;
  font-size: 24px;
}

.admin-user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.admin-name {
  color: #666;
  font-size: 14px;
}

.logout-btn {
  padding: 8px 20px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: #c0392b;
}

.admin-content {
  padding: 40px;
}

.admin-content p {
  color: #666;
  font-size: 16px;
}
</style>
