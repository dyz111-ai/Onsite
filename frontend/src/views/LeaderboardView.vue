<template>
  <div class="leaderboard-container">
    <h1>排行榜</h1>
    
    <!-- 总分排行榜 -->
    <div class="leaderboard-section">
      <h2>总分排行榜</h2>
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
            <tr v-if="loading.totalScore" class="loading-row">
              <td colspan="5">加载中...</td>
            </tr>
            <tr v-else-if="error.totalScore" class="error-row">
              <td colspan="5">{{ error.totalScore }}</td>
            </tr>
            <tr v-else-if="leaderboardData.totalScore.length === 0" class="empty-row">
              <td colspan="5">暂无数据</td>
            </tr>
            <tr v-for="item in leaderboardData.totalScore" :key="'total-' + item.user_id" class="leaderboard-row">
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
    
    <!-- 训练成本排行榜 -->
    <div class="leaderboard-section">
      <h2>训练成本排行榜</h2>
      <div class="leaderboard-table-container">
        <table class="leaderboard-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>用户ID</th>
              <th>用户账户</th>
              <th>最低成本</th>
              <th>提交时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading.cost" class="loading-row">
              <td colspan="5">加载中...</td>
            </tr>
            <tr v-else-if="error.cost" class="error-row">
              <td colspan="5">{{ error.cost }}</td>
            </tr>
            <tr v-else-if="leaderboardData.cost.length === 0" class="empty-row">
              <td colspan="5">暂无数据</td>
            </tr>
            <tr v-for="item in leaderboardData.cost" :key="'cost-' + item.user_id" class="leaderboard-row">
              <td class="rank">{{ item.rank }}</td>
              <td class="user-id">{{ item.user_id }}</td>
              <td class="account">{{ item.account }}</td>
              <td class="cost">{{ item.cost }}</td>
              <td class="submission-time">{{ formatDate(item.created_time) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 测试分数排行榜 -->
    <div class="leaderboard-section">
      <h2>测试分数排行榜</h2>
      <div class="leaderboard-table-container">
        <table class="leaderboard-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>用户ID</th>
              <th>用户账户</th>
              <th>最高测试分数</th>
              <th>提交时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading.testScore" class="loading-row">
              <td colspan="5">加载中...</td>
            </tr>
            <tr v-else-if="error.testScore" class="error-row">
              <td colspan="5">{{ error.testScore }}</td>
            </tr>
            <tr v-else-if="leaderboardData.testScore.length === 0" class="empty-row">
              <td colspan="5">暂无数据</td>
            </tr>
            <tr v-for="item in leaderboardData.testScore" :key="'test-' + item.user_id" class="leaderboard-row">
              <td class="rank">{{ item.rank }}</td>
              <td class="user-id">{{ item.user_id }}</td>
              <td class="account">{{ item.account }}</td>
              <td class="test-score">{{ item.test_score }}</td>
              <td class="submission-time">{{ formatDate(item.created_time) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLeaderboardData, getCostLeaderboardData, getTestScoreLeaderboardData } from '../api/leaderboard'

// 状态管理
const loading = ref({
  totalScore: false,
  cost: false,
  testScore: false
})

const error = ref({
  totalScore: '',
  cost: '',
  testScore: ''
})

const leaderboardData = ref({
  totalScore: [],
  cost: [],
  testScore: []
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 获取总分排行榜数据
const fetchTotalScoreLeaderboard = async () => {
  loading.value.totalScore = true
  error.value.totalScore = ''
  
  try {
    const response = await getLeaderboardData()
    leaderboardData.value.totalScore = response.data
  } catch (err) {
    error.value.totalScore = err.response?.data?.error || '获取总分排行榜数据失败'
  } finally {
    loading.value.totalScore = false
  }
}

// 获取成本排行榜数据
const fetchCostLeaderboard = async () => {
  loading.value.cost = true
  error.value.cost = ''
  
  try {
    const response = await getCostLeaderboardData()
    leaderboardData.value.cost = response.data
  } catch (err) {
    error.value.cost = err.response?.data?.error || '获取成本排行榜数据失败'
  } finally {
    loading.value.cost = false
  }
}

// 获取测试分数排行榜数据
const fetchTestScoreLeaderboard = async () => {
  loading.value.testScore = true
  error.value.testScore = ''
  
  try {
    const response = await getTestScoreLeaderboardData()
    leaderboardData.value.testScore = response.data
  } catch (err) {
    error.value.testScore = err.response?.data?.error || '获取测试分数排行榜数据失败'
  } finally {
    loading.value.testScore = false
  }
}

// 获取所有排行榜数据
const fetchAllLeaderboardData = async () => {
  await Promise.all([
    fetchTotalScoreLeaderboard(),
    fetchCostLeaderboard(),
    fetchTestScoreLeaderboard()
  ])
}

// 组件挂载时获取数据
onMounted(() => {
  fetchAllLeaderboardData()
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

.leaderboard-section {
  margin-bottom: 40px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.leaderboard-section h2 {
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
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

.cost {
  font-weight: 600;
  color: #27ae60;
  width: 120px;
}

.test-score {
  font-weight: 600;
  color: #f39c12;
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