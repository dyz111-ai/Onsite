<template>
  <div class="evaluation-view">
    <h2>测试评估</h2>
    
    <div class="filter-group">
      <select v-model="filterStatus" class="filter-select">
        <option value="">全部状态</option>
        <option value="Training">训练中</option>
        <option value="Trained">训练完成</option>
        <option value="Testing">测试中</option>
        <option value="Tested">测试完成</option>
      </select>
      
      <select v-model="filterTime" class="filter-select">
        <option value="">全部时间</option>
        <option value="today">今天</option>
        <option value="week">最近7天</option>
        <option value="month">最近30天</option>
      </select>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <div v-else-if="filteredRecords.length === 0 && trainingRecords.length === 0" class="empty-message">
      <p>暂无训练记录</p>
    </div>
    
    <div v-else-if="filteredRecords.length === 0" class="empty-message">
      <p>没有符合条件的训练记录</p>
    </div>
    
    <div v-else class="records-section">
      <h3>训练记录列表 ({{ filteredRecords.length }})</h3>
      <div class="records-table">
        <table>
          <thead>
            <tr>
              <th>训练ID</th>
              <th>状态</th>
              <th>渲染成本</th>
              <th>训练成本</th>
              <th>测试分数</th>
              <th>总分</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in filteredRecords" :key="record.training_id">
              <td>{{ record.training_id }}</td>
              <td>
                <span :class="['status-badge', getStatusClass(record.status)]">
                  {{ getStatusText(record.status) }}
                </span>
              </td>
              <td>{{ record.render_cost || 0 }}</td>
              <td>{{ record.train_cost || 0 }}</td>
              <td>{{ record.test_score || '-' }}</td>
              <td>{{ record.total_score || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTrainingRecords } from '../api/trainingRecords'

const trainingRecords = ref([])
const loading = ref(true)
const filterStatus = ref('')
const filterTime = ref('')

const getStatusText = (status) => {
  const statusMap = {
    'Training': '训练中',
    'Trained': '训练完成',
    'Testing': '测试中',
    'Tested': '测试完成'
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  const classMap = {
    'Training': 'status-training',
    'Trained': 'status-trained',
    'Testing': 'status-testing',
    'Tested': 'status-tested'
  }
  return classMap[status] || ''
}

const filteredRecords = computed(() => {
  let records = [...trainingRecords.value]
  
  // 按状态筛选
  if (filterStatus.value) {
    records = records.filter(r => r.status === filterStatus.value)
  }
  
  // 按时间筛选
  if (filterTime.value) {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    
    records = records.filter(r => {
      const recordDate = new Date(r.created_time)
      const diffTime = now - recordDate
      const diffDays = diffTime / (1000 * 60 * 60 * 24)
      
      switch (filterTime.value) {
        case 'today':
          return recordDate >= today
        case 'week':
          return diffDays <= 7
        case 'month':
          return diffDays <= 30
        default:
          return true
      }
    })
  }
  
  return records
})

const loadTrainingRecords = async () => {
  try {
    loading.value = true
    const result = await getTrainingRecords()
    trainingRecords.value = result.data || []
  } catch (error) {
    console.error('加载训练记录失败:', error)
    trainingRecords.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTrainingRecords()
})
</script>

<style scoped>
.evaluation-view {
  padding: 2rem;
  min-height: 100vh;
  width: 100%;
  background: #f5f5f5;
}

h2 {
  color: #333;
  margin-bottom: 1.5rem;
}

h3 {
  color: #555;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.filter-group {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  background: white;
  transition: border-color 0.3s;
}

.filter-select:hover {
  border-color: #42b983;
}

.filter-select:focus {
  outline: none;
  border-color: #42b983;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b983;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  margin-top: 1rem;
  color: #666;
}

.empty-message {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.empty-message p {
  color: #999;
  font-size: 1.1rem;
}

.records-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.records-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
}

th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #dee2e6;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  color: #333;
}

tbody tr:hover {
  background: #f8f9fa;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-training {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-trained {
  background: #fff3e0;
  color: #e65100;
}

.status-testing {
  background: #e3f2fd;
  color: #1565c0;
}

.status-tested {
  background: #f3e5f5;
  color: #6a1b9a;
}

.no-competition {
  color: #999;
  font-style: italic;
}
</style>
