<template>
  <div class="leaderboard-container">
    <h1>排行榜</h1>
    
    <!-- 排行榜表格 -->
    <div class="leaderboard-table-container">
      <table class="leaderboard-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>用户ID</th>
            <th>用户账户</th>
            <th>最高分数</th>
            <th>提交时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" class="loading-row">
            <td colspan="5">加载中...</td>
          </tr>
          <tr v-else-if="error" class="error-row">
            <td colspan="5">{{ error }}</td>
          </tr>
          <tr v-else-if="leaderboardData.length === 0" class="empty-row">
            <td colspan="5">暂无数据</td>
          </tr>
          <tr v-for="item in leaderboardData" :key="item.user_id" class="leaderboard-row">
            <td class="rank">{{ item.rank }}</td>
            <td class="user-id">{{ item.user_id }}</td>
            <td class="account">{{ item.account }}</td>
            <td class="score">{{ item.score }}</td>
            <td class="submission-time">{{ formatDate(item.created_time) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLeaderboardData } from '../api/leaderboard'

// 状态管理
const loading = ref(false)
const error = ref('')
const leaderboardData = ref([])

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 获取排行榜数据
const fetchLeaderboardData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await getLeaderboardData()
    leaderboardData.value = response.data
  } catch (err) {
    error.value = err.response?.data?.error || '获取排行榜数据失败'
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchLeaderboardData()
})
</script>

<style scoped>
.leaderboard-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 20px;
  color: #333;
  font-size: 24px;
}

.leaderboard-table-container {
  overflow-x: auto;
  background: white;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
}

.leaderboard-table th,
.leaderboard-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.leaderboard-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.leaderboard-row:hover {
  background: #f8f9fa;
}

.rank {
  font-weight: 600;
  color: #667eea;
  width: 80px;
}

.user-id {
  width: 120px;
}

.account {
  width: 200px;
}

.score {
  font-weight: 600;
  color: #e74c3c;
  width: 120px;
}

.submission-time {
  width: 180px;
}

.loading-row,
.error-row,
.empty-row {
  text-align: center;
  padding: 40px;
  color: #666;
  font-style: italic;
}

.error-row {
  color: #e74c3c;
}
</style>