<template>
  <div class="training-view">
    <h2>训练与监控界面</h2>
    
    <button @click="showCreateDialog" class="create-btn">
      新增训练
    </button>
    
    <button @click="downloadImage" class="download-btn">
      镜像下载
    </button>
    
    <div class="filter-group">
      <input 
        v-model="searchTrainingId" 
        type="text" 
        placeholder="搜索训练ID" 
        class="search-input"
      />
      <input 
        v-model="searchDate" 
        type="date" 
        placeholder="搜索创建日期" 
        class="search-input"
      />
      <select v-model="filterStatus" class="filter-select">
        <option value="">全部状态</option>
        <option value="Training">训练中</option>
        <option value="Trained">训练完成</option>
      </select>
      
      <select v-model="filterTime" class="filter-select">
        <option value="">全部时间</option>
        <option value="today">今天</option>
        <option value="week">最近7天</option>
        <option value="month">最近30天</option>
      </select>
      
      <button @click="clearFilters" class="clear-btn">
        清空筛选
      </button>
    </div>

    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 训练记录列表 -->
    <div v-else-if="filteredRecords.length > 0" class="records-section">
      <h3>训练记录 ({{ filteredRecords.length }})</h3>
      <div class="records-container">
        <div class="records-list">
          <div v-for="record in filteredRecords" :key="record.id" class="record-card">
            <div class="record-header">
              <div class="record-info">
                <div class="record-field">
                  <strong>训练ID：</strong>{{ record.training_id }}
                </div>
                <div class="record-field-group">
                  <div class="record-field">
                    <strong>创建时间：</strong>{{ record.createdAt }}
                  </div>
                  <div class="record-field">
                    <strong>结束时间：</strong>{{ record.end_time || '-' }}
                  </div>
                </div>
                <div class="record-field">
                  <strong>状态：</strong>
                  <span :class="['status-badge', getStatusClass(record.status)]">
                    {{ getStatusText(record.status) }}
                  </span>
                </div>
                <div class="record-field">
                  <strong>数据集数量：</strong>{{ record.dataset_count || 0 }}
                </div>
                <div class="record-field">
                  <strong>训练成本：</strong>{{ record.train_cost }}
                </div>
              </div>
              <div class="record-actions">
                <div class="action-btn-group">
                  <button @click="viewDatasets(record.training_id)" class="action-btn dataset-btn">
                    数据集信息
                  </button>
                  <button @click="viewTrainingInfo(record.training_id)" class="action-btn info-btn">
                    训练信息
                  </button>
                </div>
                <div class="action-btn-group">
                  <button @click="viewMonitor(record.training_id)" class="action-btn monitor-btn">
                    查看监控
                  </button>
                  <button @click="viewTrainingLog(record.training_id)" class="action-btn log-btn">
                    查看日志
                  </button>
                </div>
                <button @click="deleteRecord(record.id)" class="action-btn delete-btn">
                  删除
                </button>
              </div>
            </div>
            
            <!-- 实时训练日志（仅训练中显示） -->
            <div v-if="record.logs && record.logs.length > 0 && record.status === 'Training'" class="log-section">
              <div class="log-header">
                <h4>执行进度</h4>
                <button @click="toggleLogs(record.training_id)" class="toggle-logs-btn">
                  {{ record.showLogs ? '隐藏' : '显示' }}
                </button>
              </div>
              <div v-if="record.showLogs" class="log-container" :ref="el => setLogRef(record.training_id, el)">
                <div v-for="(log, index) in record.logs" :key="index" class="log-line">
                  {{ log }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无筛选结果 -->
    <div v-else-if="!loading && trainingRecords.length > 0 && filteredRecords.length === 0" class="no-data">
      没有符合条件的训练记录
    </div>

    <!-- 训练信息弹窗 -->
    <TrainingInfoDialog 
      :show="showTrainingInfoDialog"
      :training-id="currentTrainingInfoId"
      @close="closeTrainingInfoDialog"
    />

    <!-- 其他弹窗 -->
    <TrainingDialogs
      :create-dialog="createDialogData"
      :monitor-dialog="monitorDialogData"
      :log-dialog="logDialogData"
      :dataset-dialog="datasetDialogData"
      @close-create="closeDialog"
      @confirm-create="createTraining"
      @close-monitor="closeMonitorDialog"
      @close-log="closeLogDialog"
      @download-log="downloadLog"
      @close-dataset="closeDatasetDialog"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { io } from 'socket.io-client'
import axios from 'axios'
import { getTrainingRecords, deleteTrainingRecord } from '../api/trainingRecords'
import TrainingInfoDialog from '../components/TrainingInfoDialog.vue'
import TrainingDialogs from '../components/TrainingDialogs.vue'

const message = ref('')
const messageType = ref('info')
const trainingRecords = ref([])
const loading = ref(true)
const logRefs = ref({})
const filterStatus = ref('')
const filterTime = ref('')
const searchTrainingId = ref('')
const searchDate = ref('')
let socket = null
const activeTrainingIds = new Set()

// 训练信息弹窗
const showTrainingInfoDialog = ref(false)
const currentTrainingInfoId = ref(null)

// 新增训练弹窗数据
const createDialogData = ref({
  show: false,
  loading: false,
  creating: false,
  renders: [],
  selectedIds: []
})

// 监控弹窗数据
const monitorDialogData = ref({
  show: false,
  loading: false,
  error: '',
  trainingId: null,
  data: []
})

// 日志弹窗数据
const logDialogData = ref({
  show: false,
  loading: false,
  error: '',
  trainingId: null,
  content: ''
})

// 数据集弹窗数据
const datasetDialogData = ref({
  show: false,
  loading: false,
  error: '',
  trainingId: null,
  datasets: []
})

// 筛选后的记录
const filteredRecords = computed(() => {
  let records = trainingRecords.value
  
  // 按训练ID搜索
  if (searchTrainingId.value) {
    const searchId = searchTrainingId.value.trim()
    records = records.filter(r => 
      String(r.training_id).includes(searchId)
    )
  }
  
  // 按创建日期搜索（精确到日）
  if (searchDate.value) {
    records = records.filter(r => {
      const recordDate = (r.created_time || r.createdAt || '').split(' ')[0]
      return recordDate === searchDate.value
    })
  }
  
  if (filterStatus.value) {
    records = records.filter(r => r.status === filterStatus.value)
  }
  
  if (filterTime.value) {
    const now = new Date()
    records = records.filter(r => {
      const createdTime = new Date(r.created_time || r.createdAt)
      const diffDays = Math.floor((now - createdTime) / (1000 * 60 * 60 * 24))
      
      if (filterTime.value === 'today') {
        return diffDays === 0
      } else if (filterTime.value === 'week') {
        return diffDays <= 7
      } else if (filterTime.value === 'month') {
        return diffDays <= 30
      }
      return true
    })
  }
  
  return records
})

const clearFilters = () => {
  searchTrainingId.value = ''
  searchDate.value = ''
  filterStatus.value = ''
  filterTime.value = ''
}

const setLogRef = (id, el) => {
  if (el) {
    logRefs.value[id] = el
  }
}

const scrollToBottom = (recordId) => {
  nextTick(() => {
    const logContainer = logRefs.value[recordId]
    if (logContainer) {
      logContainer.scrollTop = logContainer.scrollHeight
    }
  })
}

const toggleLogs = (trainingId) => {
  const record = trainingRecords.value.find(r => r.training_id === trainingId)
  if (record) {
    record.showLogs = !record.showLogs
    if (record.showLogs) {
      scrollToBottom(trainingId)
    }
  }
}

// 加载训练记录
const loadTrainingRecords = async () => {
  loading.value = true
  try {
    const result = await getTrainingRecords()
    
    const oldRecordsMap = {}
    trainingRecords.value.forEach(record => {
      oldRecordsMap[record.training_id] = {
        logs: record.logs || [],
        showLogs: record.showLogs || false
      }
    })
    
    trainingRecords.value = (result.data || []).map(record => {
      const oldRecord = oldRecordsMap[record.training_id]
      return {
        ...record,
        logs: oldRecord ? oldRecord.logs : [],
        showLogs: oldRecord ? oldRecord.showLogs : false
      }
    })
  } catch (error) {
    message.value = '加载训练记录失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
    trainingRecords.value = []
  } finally {
    loading.value = false
  }
}

// 刷新单条训练记录
const refreshSingleRecord = async (trainingId) => {
  try {
    const response = await axios.get(`/api/training/records/${trainingId}`)
    const updatedRecord = response.data.data
    
    const index = trainingRecords.value.findIndex(r => r.training_id === trainingId)
    if (index !== -1) {
      const oldRecord = trainingRecords.value[index]
      trainingRecords.value[index] = {
        ...updatedRecord,
        logs: oldRecord.logs || [],
        showLogs: oldRecord.showLogs || false
      }
    }
  } catch (error) {
    console.error('刷新训练记录失败:', error)
  }
}

// 新增训练弹窗
const showCreateDialog = async () => {
  createDialogData.value.show = true
  createDialogData.value.selectedIds = []
  createDialogData.value.loading = true
  
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/render/records?for_training=true', {
      headers: { Authorization: `Bearer ${token}` }
    })
    createDialogData.value.renders = response.data.data || []
  } catch (error) {
    console.error('加载数据集失败:', error)
    createDialogData.value.renders = []
  } finally {
    createDialogData.value.loading = false
  }
}

const closeDialog = () => {
  createDialogData.value.show = false
  createDialogData.value.selectedIds = []
  createDialogData.value.creating = false
}

const downloadImage = () => {
  try {
    message.value = '正在启动下载...'
    messageType.value = 'info'
    
    const token = localStorage.getItem('token')
    const link = document.createElement('a')
    link.href = `/api/training/download-image?token=${token}`
    link.download = 'Onsite-image.tar'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    message.value = '文件已开始下载，请在浏览器中查看下载进度'
    messageType.value = 'success'
  } catch (error) {
    console.error('下载镜像失败:', error)
    message.value = '下载镜像失败：' + error.message
    messageType.value = 'error'
  }
}

const createTraining = async (selectedIds) => {
  if (selectedIds.length === 0) return
  
  createDialogData.value.creating = true
  
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post('/api/training/records', {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const trainingId = response.data.data.training_id
    
    // 使用正确的API路径，一次性提交所有render_ids
    await axios.post(`/api/render/training/${trainingId}/relation`, {
      render_ids: selectedIds
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    message.value = '训练创建成功，正在启动训练...'
    messageType.value = 'success'
    closeDialog()
    await loadTrainingRecords()
    
    // 启动训练
    activeTrainingIds.add(trainingId)
    await axios.post('/api/training/start', {
      training_id: trainingId
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    message.value = `训练 ${trainingId} 已启动`
    messageType.value = 'success'
  } catch (error) {
    message.value = '创建失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
  } finally {
    createDialogData.value.creating = false
  }
}

const deleteRecord = async (recordId) => {
  if (!confirm('确定要删除这条训练记录吗？')) {
    return
  }
  
  try {
    await deleteTrainingRecord(recordId)
    await loadTrainingRecords()
    
    message.value = '训练记录已删除'
    messageType.value = 'success'
  } catch (error) {
    message.value = '删除失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
  }
}

// 查看监控
const viewMonitor = async (trainingId) => {
  monitorDialogData.value.trainingId = trainingId
  monitorDialogData.value.error = ''
  monitorDialogData.value.data = []
  monitorDialogData.value.show = true
  
  await nextTick()
  await nextTick()
  
  monitorDialogData.value.loading = true
  
  try {
    const response = await axios.get(`/api/training/monitor/${trainingId}`)
    monitorDialogData.value.data = response.data.data
    
    if (monitorDialogData.value.data.length === 0) {
      monitorDialogData.value.error = '暂无监控数据'
    }
  } catch (error) {
    console.error('加载监控数据失败:', error)
    monitorDialogData.value.error = error.response?.data?.error || '加载监控数据失败'
  } finally {
    monitorDialogData.value.loading = false
  }
}

const closeMonitorDialog = () => {
  monitorDialogData.value.show = false
}

// 查看训练信息
const viewTrainingInfo = (trainingId) => {
  currentTrainingInfoId.value = trainingId
  showTrainingInfoDialog.value = true
}

const closeTrainingInfoDialog = () => {
  showTrainingInfoDialog.value = false
  currentTrainingInfoId.value = null
}

// 查看训练日志
const viewTrainingLog = async (trainingId) => {
  logDialogData.value.trainingId = trainingId
  logDialogData.value.error = ''
  logDialogData.value.content = ''
  logDialogData.value.show = true
  logDialogData.value.loading = true
  
  try {
    const response = await axios.get(`/api/training/logs/${trainingId}`)
    logDialogData.value.content = response.data.data
  } catch (error) {
    console.error('加载训练日志失败:', error)
    logDialogData.value.error = error.response?.data?.error || '加载训练日志失败'
  } finally {
    logDialogData.value.loading = false
  }
}

const closeLogDialog = () => {
  logDialogData.value.show = false
  logDialogData.value.content = ''
  logDialogData.value.trainingId = null
}

const downloadLog = (content) => {
  if (!content) return
  
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `train${logDialogData.value.trainingId}_log.txt`
  
  document.body.appendChild(link)
  link.click()
  
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// 查看数据集
const viewDatasets = async (trainingId) => {
  datasetDialogData.value.trainingId = trainingId
  datasetDialogData.value.error = ''
  datasetDialogData.value.datasets = []
  datasetDialogData.value.show = true
  datasetDialogData.value.loading = true
  
  try {
    const response = await axios.get(`/api/render/training/${trainingId}`)
    datasetDialogData.value.datasets = response.data.data
  } catch (error) {
    console.error('加载数据集信息失败:', error)
    datasetDialogData.value.error = error.response?.data?.error || '加载数据集信息失败'
  } finally {
    datasetDialogData.value.loading = false
  }
}

const closeDatasetDialog = () => {
  datasetDialogData.value.show = false
  datasetDialogData.value.datasets = []
  datasetDialogData.value.trainingId = null
}

const getStatusClass = (status) => {
  const statusMap = {
    'Training': 'status-training',
    'Trained': 'status-trained',
    'Testing': 'status-testing',
    'Tested': 'status-tested'
  }
  return statusMap[status] || 'status-default'
}

const getStatusText = (status) => {
  const textMap = {
    'Training': '训练中',
    'Trained': '训练完成',
    'Testing': '测试中',
    'Tested': '测试完成'
  }
  return textMap[status] || status
}

onMounted(() => {
  loadTrainingRecords()
  
  socket = io('http://localhost:8000')

  socket.on('connect', () => {
    console.log('WebSocket已连接')
  })

  socket.on('training_log', (data) => {
    console.log('收到日志:', data)
    const trainingId = data.training_id
    if (trainingId && activeTrainingIds.has(trainingId)) {
      const record = trainingRecords.value.find(r => r.training_id === trainingId)
      if (record) {
        if (!record.logs) {
          record.logs = []
        }
        record.logs.push(data.message)
        if (record.showLogs) {
          scrollToBottom(trainingId)
        }
      }
    }
  })

  socket.on('training_complete', async (data) => {
    console.log('训练完成:', data)
    const trainingId = data.training_id
    if (trainingId && activeTrainingIds.has(trainingId)) {
      const record = trainingRecords.value.find(r => r.training_id === trainingId)
      if (record) {
        if (data.status === 'success') {
          message.value = `训练 ${trainingId} 完成！`
          messageType.value = 'success'
          
          await refreshSingleRecord(trainingId)
        } else {
          message.value = `训练 ${trainingId} 失败：${data.message}`
          messageType.value = 'error'
        }
      }
      activeTrainingIds.delete(trainingId)
    }
  })

  socket.on('disconnect', () => {
    console.log('WebSocket已断开')
  })
})

onUnmounted(() => {
  if (socket) {
    socket.disconnect()
  }
})
</script>

<style scoped>
.training-view {
  padding: 2rem;
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

h2 {
  color: #333;
  margin-bottom: 1.5rem;
}

.create-btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  background: #764ba2;
  color: white;
  cursor: pointer;
  transition: opacity 0.3s;
  margin-bottom: 1rem;
  min-width: 140px;
  height: 45px;
}

.create-btn:hover {
  opacity: 0.9;
}

.download-btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  background: #007bff;
  color: white;
  cursor: pointer;
  transition: opacity 0.3s;
  margin-bottom: 1rem;
  margin-left: 0.5rem;
  min-width: 140px;
  height: 45px;
}

.download-btn:hover {
  opacity: 0.9;
}

.download-btn:hover {
  opacity: 0.9;
}

.filter-group {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-input {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  background: white;
  transition: border-color 0.3s;
  min-width: 150px;
}

.search-input:hover {
  border-color: #9c27b0;
}

.search-input:focus {
  outline: none;
  border-color: #9c27b0;
}

.search-input::placeholder {
  color: #999;
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
  border-color: #9c27b0;
}

.filter-select:focus {
  outline: none;
  border-color: #9c27b0;
}

.clear-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  background: white;
  color: #666;
  transition: all 0.3s;
}

.clear-btn:hover {
  background: #f5f5f5;
  border-color: #999;
}

.message {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.message.info {
  background: #e3f2fd;
  color: #1976d2;
}

.message.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.message.error {
  background: #ffebee;
  color: #c62828;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #9c27b0;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.records-section {
  margin-bottom: 2rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.records-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 1.5rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

h3 {
  color: #333;
  margin-bottom: 1rem;
}

h4 {
  color: #555;
  margin: 1rem 0 0.5rem 0;
  font-size: 1rem;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.record-card {
  background: #fafafa;
  padding: 1.5rem;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  border-left: 4px solid #9c27b0;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
  transition: box-shadow 0.3s;
  flex-shrink: 0;
}

.record-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.record-info {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  flex: 1;
}

.record-field-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.record-field {
  color: #555;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-training {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-trained {
  background: #fff3e0;
  color: #f57c00;
}

.status-testing {
  background: #e3f2fd;
  color: #1976d2;
}

.status-tested {
  background: #f3e5f5;
  color: #7b1fa2;
}

.status-default {
  background: #f5f5f5;
  color: #666;
}

.record-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.record-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: flex-start;
}

.action-btn-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: opacity 0.3s;
  white-space: nowrap;
  outline: none;
}

.action-btn:hover {
  opacity: 0.85;
}

.action-btn:focus {
  outline: none;
}

.monitor-btn {
  background: #007bff;
  color: white;
}

.log-btn {
  background: #007bff;
  color: white;
}

.dataset-btn {
  background: #17a2b8;
  color: white;
}

.info-btn {
  background: #17a2b8;
  color: white;
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.log-section {
  margin-top: 1rem;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.log-header h4 {
  margin: 0;
}

.toggle-logs-btn {
  padding: 0.4rem 1rem;
  border: 1px solid #9c27b0;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
  color: #9c27b0;
}

.toggle-logs-btn:hover {
  background: #9c27b0;
  color: white;
}

.log-container {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 1rem;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.log-line {
  padding: 0.25rem 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.no-data {
  text-align: center;
  padding: 3rem;
  color: #999;
  font-size: 1.1rem;
}
</style>
