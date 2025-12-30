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
              <th>测试赛题</th>
              <th>操作</th>
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
              <td>
                <span v-if="record.competition_type && record.competition_number">
                  {{ record.competition_type }}-{{ record.competition_number }}
                </span>
                <span v-else class="no-competition">未选择</span>
              </td>
              <td>
                <button @click="showCompetitionDialog(record.training_id)" class="select-btn">
                  选择测试赛题
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 选择赛题弹窗 -->
    <div v-if="showDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>选择测试赛题</h3>
          <button @click="closeDialog" class="close-btn">&times;</button>
        </div>
        
        <div v-if="loadingCompetitions" class="dialog-loading">
          <div class="loading-spinner"></div>
          <p>加载赛题中...</p>
        </div>
        
        <div v-else-if="competitions.length === 0" class="dialog-empty">
          <p>暂无可用赛题</p>
        </div>
        
        <div v-else class="dialog-body">
          <!-- 类型选择标签 -->
          <div class="type-tabs">
            <button 
              v-for="type in competitionTypes" 
              :key="type"
              :class="['type-tab', { active: selectedType === type }]"
              @click="selectedType = type"
            >
              {{ type }}
            </button>
          </div>
          
          <!-- 赛题列表 -->
          <div class="competitions-list">
            <div 
              v-for="comp in filteredCompetitions" 
              :key="comp.competition_id"
              :class="['competition-item', { selected: selectedCompetitionId === comp.competition_id }]"
              @click="selectedCompetitionId = comp.competition_id"
            >
              <div class="competition-info">
                <div><strong>赛题ID：</strong>{{ comp.competition_id }}</div>
                <div><strong>类型：</strong>{{ comp.type }}</div>
                <div><strong>编号：</strong>{{ comp.number }}</div>
              </div>
            </div>
            
            <div v-if="filteredCompetitions.length === 0" class="no-competitions">
              <p>该类型暂无赛题</p>
            </div>
          </div>
        </div>
        
        <div class="dialog-footer">
          <button @click="closeDialog" class="cancel-btn">取消</button>
          <button 
            @click="confirmSelection" 
            :disabled="!selectedCompetitionId || submitting"
            class="confirm-btn"
          >
            {{ submitting ? '提交中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTrainingRecords } from '../api/trainingRecords'
import { getCompetitions, selectCompetition } from '../api/competition'

const trainingRecords = ref([])
const loading = ref(true)
const filterStatus = ref('')
const filterTime = ref('')

const showDialog = ref(false)
const competitions = ref([])
const loadingCompetitions = ref(false)
const selectedCompetitionId = ref(null)
const currentTrainingId = ref(null)
const submitting = ref(false)
const selectedType = ref('A')

// 获取所有赛题类型
const competitionTypes = computed(() => {
  const types = [...new Set(competitions.value.map(c => c.type))]
  return types.sort()
})

// 根据选中的类型筛选赛题
const filteredCompetitions = computed(() => {
  return competitions.value.filter(c => c.type === selectedType.value)
})

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

const showCompetitionDialog = async (trainingId) => {
  currentTrainingId.value = trainingId
  selectedCompetitionId.value = null
  showDialog.value = true
  
  // 加载赛题列表
  loadingCompetitions.value = true
  try {
    const result = await getCompetitions()
    competitions.value = result.data || []
    
    // 默认选择第一个类型
    if (competitions.value.length > 0) {
      const types = [...new Set(competitions.value.map(c => c.type))].sort()
      selectedType.value = types[0] || 'A'
    }
  } catch (error) {
    console.error('加载赛题失败:', error)
    competitions.value = []
  } finally {
    loadingCompetitions.value = false
  }
}

const closeDialog = () => {
  showDialog.value = false
  selectedCompetitionId.value = null
  currentTrainingId.value = null
}

const confirmSelection = async () => {
  if (!selectedCompetitionId.value || !currentTrainingId.value) return
  
  submitting.value = true
  try {
    await selectCompetition({
      training_id: currentTrainingId.value,
      competition_id: selectedCompetitionId.value
    })
    
    alert('选择赛题成功')
    closeDialog()
  } catch (error) {
    console.error('选择赛题失败:', error)
    alert(error.response?.data?.error || '选择赛题失败')
  } finally {
    submitting.value = false
  }
}

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

.select-btn {
  padding: 0.5rem 1rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.3s;
}

.select-btn:hover {
  background: #359268;
}

.select-btn:focus {
  outline: none;
}

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
}

.dialog-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #999;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 30px;
  height: 30px;
}

.close-btn:hover {
  color: #333;
}

.dialog-loading,
.dialog-empty {
  padding: 3rem;
  text-align: center;
}

.dialog-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.type-tabs {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  background: #f8f9fa;
}

.type-tab {
  padding: 0.5rem 1.5rem;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.type-tab:hover {
  border-color: #42b983;
  background: #f8f9fa;
}

.type-tab.active {
  background: #42b983;
  color: white;
  border-color: #42b983;
}

.competitions-list {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.no-competitions {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.competition-item {
  padding: 1rem;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.competition-item:hover {
  border-color: #42b983;
  background: #f8f9fa;
}

.competition-item.selected {
  border-color: #42b983;
  background: #e8f5e9;
}

.competition-info div {
  margin-bottom: 0.5rem;
  color: #555;
}

.competition-info div:last-child {
  margin-bottom: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #dee2e6;
}

.cancel-btn,
.confirm-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
}

.cancel-btn {
  background: #f8f9fa;
  color: #555;
}

.cancel-btn:hover {
  background: #e9ecef;
}

.confirm-btn {
  background: #42b983;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: #359268;
}

.confirm-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
