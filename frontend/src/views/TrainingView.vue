<template>
  <div class="training-view">
    <h2>训练</h2>
    
    <button @click="showCreateDialog" class="create-btn">
      新增训练
    </button>
    
    <button @click="downloadImage" class="download-btn">
      镜像下载
    </button>
    
    <div class="filter-group">
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
                <div class="record-field">
                  <strong>创建时间：</strong>{{ record.createdAt }}
                </div>
                <div class="record-field">
                  <strong>状态：</strong>
                  <span :class="['status-badge', getStatusClass(record.status)]">
                    {{ getStatusText(record.status) }}
                  </span>
                </div>
                <div class="record-field">
                  <strong>训练成本：</strong>{{ record.train_cost }}
                </div>
                <div class="record-field">
                  <strong>测试分数：</strong>{{ record.test_score }}
                </div>
              </div>
              <div class="record-actions">
                <button @click="viewDatasets(record.training_id)" class="dataset-btn">
                  数据集信息
                </button>
                <button @click="viewMonitor(record.training_id)" class="monitor-btn">
                  查看监控
                </button>
                <button @click="viewTrainingLog(record.training_id)" class="log-btn">
                  查看日志
                </button>
                <button @click="deleteRecord(record.id)" class="delete-btn">
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

    <!-- 新增训练弹窗 -->
    <div v-if="showDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content create-dialog" @click.stop>
        <div class="dialog-header">
          <h3>新增训练</h3>
          <button class="close-btn" @click="closeDialog">×</button>
        </div>
        <div class="dialog-body">
          <div v-if="renderLoading" class="loading">加载数据集中...</div>
          <div v-else-if="renderRecords.length === 0" class="no-data">暂无可用数据集</div>
          <div v-else class="render-selection">
            <h4>选择数据集</h4>
            <div class="render-list">
              <div v-for="render in renderRecords" :key="render.render_id" class="render-item">
                <label class="render-checkbox">
                  <input 
                    type="checkbox" 
                    :value="render.render_id" 
                    v-model="selectedRenderIds"
                  />
                  <div class="render-info">
                    <div><strong>名称：</strong>{{ render.name || '未命名' }}</div>
                    <div><strong>状态：</strong>{{ render.status }}</div>
                    <div><strong>创建时间：</strong>{{ render.created_time }}</div>
                  </div>
                </label>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="closeDialog" class="cancel-btn">取消</button>
          <button @click="createTraining" class="confirm-btn" :disabled="selectedRenderIds.length === 0">
            确定 (已选 {{ selectedRenderIds.length }})
          </button>
        </div>
      </div>
    </div>
    <!-- 监控图表弹窗 -->
    <div v-if="showMonitorDialog" class="dialog-overlay" @click="closeMonitorDialog">
      <div class="dialog-content monitor-dialog" @click.stop>
        <div class="dialog-header">
          <h3>训练监控 - ID: {{ currentMonitorId }}</h3>
          <button class="close-btn" @click="closeMonitorDialog">×</button>
        </div>
        <div class="dialog-body">
          <div v-if="monitorLoading" class="loading">加载中...</div>
          <div v-else-if="monitorError" class="error-message">{{ monitorError }}</div>
          <div v-else-if="monitorData.length === 0" class="no-data">暂无监控数据</div>
          <div v-else class="charts-container">
            <!-- CPU 使用率图表 -->
            <div class="chart-item">
              <h4>CPU 使用率 (秒)</h4>
              <canvas ref="cpuChart"></canvas>
            </div>
            
            <!-- GPU 利用率图表 -->
            <div class="chart-item">
              <h4>GPU 利用率 (%)</h4>
              <canvas ref="gpuChart"></canvas>
            </div>
            
            <!-- 内存使用图表 -->
            <div class="chart-item">
              <h4>内存使用 (MB)</h4>
              <canvas ref="memoryChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 训练日志弹窗 -->
    <div v-if="showLogDialog" class="dialog-overlay" @click="closeLogDialog">
      <div class="dialog-content log-dialog" @click.stop>
        <div class="dialog-header">
          <h3>训练日志 - ID: {{ currentLogId }}</h3>
          <div class="header-actions">
            <button v-if="!logLoading && !logError" @click="downloadLog" class="download-btn">
              下载日志
            </button>
            <button class="close-btn" @click="closeLogDialog">×</button>
          </div>
        </div>
        <div class="dialog-body">
          <div v-if="logLoading" class="loading">加载中...</div>
          <div v-else-if="logError" class="error-message">{{ logError }}</div>
          <div v-else class="log-content">
            <pre>{{ logContent }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据集信息弹窗 -->
    <div v-if="showDatasetDialog" class="dialog-overlay" @click="closeDatasetDialog">
      <div class="dialog-content dataset-dialog" @click.stop>
        <div class="dialog-header">
          <h3>数据集信息 - 训练ID: {{ currentDatasetTrainingId }}</h3>
          <button class="close-btn" @click="closeDatasetDialog">×</button>
        </div>
        <div class="dialog-body">
          <div v-if="datasetLoading" class="loading">加载中...</div>
          <div v-else-if="datasetError" class="error-message">{{ datasetError }}</div>
          <div v-else-if="datasetRecords.length === 0" class="no-data">该训练未关联数据集</div>
          <div v-else class="dataset-list">
            <div v-for="dataset in datasetRecords" :key="dataset.render_id" class="dataset-item">
              <div class="dataset-field"><strong>名称：</strong>{{ dataset.name || '未命名' }}</div>
              <div class="dataset-field"><strong>状态：</strong>{{ dataset.status }}</div>
              <div class="dataset-field"><strong>创建时间：</strong>{{ dataset.created_time }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { startTraining, getTrainingResult } from '../api/training'
import { getTrainingRecords, createTrainingRecord, updateTrainingRecord, deleteTrainingRecord } from '../api/trainingRecords'
import { io } from 'socket.io-client'
import { Chart, registerables } from 'chart.js'
import axios from 'axios'

Chart.register(...registerables)

const message = ref('')
const messageType = ref('info')
const showDialog = ref(false)
const trainingRecords = ref([])
const loading = ref(true)
const logRefs = ref({})

// 渲染数据集相关
const renderRecords = ref([])
const renderLoading = ref(false)
const selectedRenderIds = ref([])

// 数据集信息弹窗
const showDatasetDialog = ref(false)
const currentDatasetTrainingId = ref(null)
const datasetRecords = ref([])
const datasetLoading = ref(false)
const datasetError = ref('')
const filterStatus = ref('')
const filterTime = ref('')
let socket = null
// 使用 Set 追踪所有正在训练的 ID，支持并发
const activeTrainingIds = new Set()

// 筛选后的记录
const filteredRecords = computed(() => {
  let records = trainingRecords.value
  
  // 按状态筛选
  if (filterStatus.value) {
    records = records.filter(r => r.status === filterStatus.value)
  }
  
  // 按时间筛选
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

const showMonitorDialog = ref(false)
const currentMonitorId = ref(null)
const monitorData = ref([])
const monitorLoading = ref(false)
const monitorError = ref('')
const cpuChart = ref(null)
const gpuChart = ref(null)
const memoryChart = ref(null)
let cpuChartInstance = null
let gpuChartInstance = null
let memoryChartInstance = null

const showLogDialog = ref(false)
const currentLogId = ref(null)
const logContent = ref('')
const logLoading = ref(false)
const logError = ref('')

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

// 切换日志显示/隐藏
const toggleLogs = (trainingId) => {
  const record = trainingRecords.value.find(r => r.training_id === trainingId)
  if (record) {
    record.showLogs = !record.showLogs
    if (record.showLogs) {
      scrollToBottom(trainingId)
    }
  }
}

// 从服务器加载训练记录
const loadTrainingRecords = async () => {
  loading.value = true
  try {
    const result = await getTrainingRecords()
    
    // 保存旧记录的日志和展开状态
    const oldRecordsMap = {}
    trainingRecords.value.forEach(record => {
      oldRecordsMap[record.training_id] = {
        logs: record.logs || [],
        showLogs: record.showLogs || false
      }
    })
    
    // 为每条记录添加日志数组和显示状态，保留已有的日志
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
    
    // 找到对应的记录并更新，保留日志和展开状态
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

// 保存记录更新到服务器
const saveRecordUpdate = async (recordId, updateData) => {
  try {
    await updateTrainingRecord(recordId, updateData)
  } catch (error) {
    console.error('保存记录更新失败:', error)
  }
}

const showCreateDialog = async () => {
  showDialog.value = true
  selectedRenderIds.value = []
  
  // 加载渲染数据集
  renderLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/render/records', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    renderRecords.value = response.data.data
  } catch (error) {
    console.error('加载渲染数据集失败:', error)
    renderRecords.value = []
  } finally {
    renderLoading.value = false
  }
}

const closeDialog = () => {
  showDialog.value = false
}

const downloadImage = async () => {
  try {
    // 检查是否支持 File System Access API
    if ('showSaveFilePicker' in window) {
      let fileHandle = null
      
      try {
        // 先让用户选择保存位置（在用户手势的直接处理程序中）
        fileHandle = await window.showSaveFilePicker({
          suggestedName: 'Onsite-image.tar',
          types: [{
            description: 'TAR Archive',
            accept: { 'application/x-tar': ['.tar'] }
          }]
        })
      } catch (err) {
        // 用户取消了选择保存位置
        if (err.name === 'AbortError') {
          message.value = '已取消下载'
          messageType.value = 'info'
          return
        } else {
          throw err
        }
      }
      
      // 用户选择了位置，开始下载文件
      message.value = '正在下载镜像文件...'
      messageType.value = 'info'
      
      const token = localStorage.getItem('token')
      const response = await axios.get('/api/training/download-image', {
        headers: { 'Authorization': `Bearer ${token}` },
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data], { type: 'application/x-tar' })
      
      // 写入文件
      const writable = await fileHandle.createWritable()
      await writable.write(blob)
      await writable.close()
      
      message.value = '镜像文件下载成功'
      messageType.value = 'success'
    } else {
      // 回退到传统下载方式
      message.value = '正在准备下载镜像文件...'
      messageType.value = 'info'
      
      const token = localStorage.getItem('token')
      const response = await axios.get('/api/training/download-image', {
        headers: { 'Authorization': `Bearer ${token}` },
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data], { type: 'application/x-tar' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'Onsite-image.tar'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      message.value = '镜像文件下载成功（已保存到默认下载位置）'
      messageType.value = 'success'
    }
  } catch (error) {
    console.error('下载镜像失败:', error)
    message.value = '下载镜像失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
  }
}

const createTraining = async () => {
  try {
    // 创建训练记录
    const result = await createTrainingRecord()
    const trainingId = result.data.training_id
    
    // 创建训练和渲染的关联
    if (selectedRenderIds.value.length > 0) {
      try {
        await axios.post(`/api/render/training/${trainingId}/relation`, {
          render_ids: selectedRenderIds.value
        })
      } catch (error) {
        console.error('创建数据集关联失败:', error)
      }
    }
    
    // 添加到活跃训练集合
    activeTrainingIds.add(trainingId)
    
    // 直接添加新记录到列表顶部，不重新加载全部
    const newRecord = {
      ...result.data,
      logs: [],
      showLogs: false
    }
    trainingRecords.value.unshift(newRecord)
    
    closeDialog()
    
    message.value = `训练记录已创建 (ID: ${trainingId})，正在启动训练...`
    messageType.value = 'success'
    
    // 启动训练脚本，传递 training_id
    try {
      await startTraining({ training_id: trainingId })
      message.value = `训练 ${trainingId} 已启动，请查看日志`
      messageType.value = 'success'
    } catch (error) {
      message.value = '启动训练失败：' + (error.response?.data?.error || error.message)
      messageType.value = 'error'
      // 启动失败，从活跃集合中移除
      activeTrainingIds.delete(trainingId)
    }
  } catch (error) {
    message.value = '创建训练记录失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
  }
}

const createMonitorRecord = (trainingId, createdAt) => {
  // 创建监控记录
  const monitorRecord = {
    id: 'MONITOR-' + Date.now(),
    trainingId: trainingId,
    createdAt: createdAt,
    status: 'pending',
    data: []
  }
  
  // 从localStorage读取现有监控记录
  const stored = localStorage.getItem('monitorRecords')
  const monitorRecords = stored ? JSON.parse(stored) : []
  
  // 添加新记录
  monitorRecords.unshift(monitorRecord)
  
  // 保存到localStorage
  localStorage.setItem('monitorRecords', JSON.stringify(monitorRecords))
  
  // 触发storage事件通知监控页面
  window.dispatchEvent(new StorageEvent('storage', {
    key: 'monitorRecords',
    newValue: JSON.stringify(monitorRecords)
  }))
}

const handleStartTraining = async (recordId) => {
  const record = trainingRecords.value.find(r => r.id === recordId)
  if (!record) return
  
  // 如果已经完成，不允许再次训练
  if (record.status === 'completed') {
    message.value = '该训练已完成，无法重复训练'
    messageType.value = 'error'
    return
  }
  
  record.loading = true
  record.logs = []
  record.csvData = []
  record.showLogs = true
  currentTrainingId = recordId
  
  // 更新状态为running
  await saveRecordUpdate(recordId, { status: 'running', logs: [], csvData: [] })
  updateMonitorStatus(recordId, 'running')
  
  message.value = '正在启动训练脚本...'
  messageType.value = 'info'

  try {
    await startTraining()
    message.value = '训练脚本已启动，请查看日志输出'
    messageType.value = 'success'
  } catch (error) {
    message.value = '启动失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
    record.loading = false
    currentTrainingId = null
    // 更新状态为failed
    await saveRecordUpdate(recordId, { status: 'failed' })
    updateMonitorStatus(recordId, 'failed')
  }
}



const updateMonitorStatus = (trainingId, status, data = null) => {
  const stored = localStorage.getItem('monitorRecords')
  if (!stored) return
  
  const monitorRecords = JSON.parse(stored)
  const monitorRecord = monitorRecords.find(r => r.trainingId === trainingId)
  
  if (monitorRecord) {
    monitorRecord.status = status
    if (data) {
      monitorRecord.data = data
    }
    localStorage.setItem('monitorRecords', JSON.stringify(monitorRecords))
    window.dispatchEvent(new StorageEvent('storage', {
      key: 'monitorRecords',
      newValue: JSON.stringify(monitorRecords)
    }))
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

const viewMonitor = async (trainingId) => {
  currentMonitorId.value = trainingId
  monitorError.value = ''
  monitorData.value = []
  
  // 先显示弹窗，但不显示加载状态
  showMonitorDialog.value = true
  
  // 等待弹窗 DOM 渲染
  await nextTick()
  await nextTick()
  
  // 开始加载数据
  monitorLoading.value = true
  
  try {
    console.log('正在加载监控数据，training_id:', trainingId)
    const response = await axios.get(`/api/training/monitor/${trainingId}`)
    console.log('监控数据响应:', response.data)
    monitorData.value = response.data.data
    console.log('监控数据长度:', monitorData.value.length)
    
    if (monitorData.value.length === 0) {
      monitorError.value = '暂无监控数据'
      monitorLoading.value = false
      return
    }
    
    // 数据加载完成，隐藏加载状态
    monitorLoading.value = false
    
    // 等待图表容器渲染
    await nextTick()
    await nextTick()
    
    console.log('开始绘制图表')
    console.log('cpuChart ref:', cpuChart.value)
    console.log('gpuChart ref:', gpuChart.value)
    console.log('memoryChart ref:', memoryChart.value)
    
    // 使用 setTimeout 确保 DOM 完全渲染
    setTimeout(() => {
      drawCharts()
    }, 100)
  } catch (error) {
    console.error('加载监控数据失败:', error)
    monitorError.value = error.response?.data?.error || '加载监控数据失败'
    monitorLoading.value = false
  }
}

const closeMonitorDialog = () => {
  showMonitorDialog.value = false
  if (cpuChartInstance) cpuChartInstance.destroy()
  if (gpuChartInstance) gpuChartInstance.destroy()
  if (memoryChartInstance) memoryChartInstance.destroy()
}

const viewTrainingLog = async (trainingId) => {
  currentLogId.value = trainingId
  logError.value = ''
  logContent.value = ''
  showLogDialog.value = true
  logLoading.value = true
  
  try {
    const response = await axios.get(`/api/training/logs/${trainingId}`)
    logContent.value = response.data.data
    logLoading.value = false
  } catch (error) {
    console.error('加载训练日志失败:', error)
    logError.value = error.response?.data?.error || '加载训练日志失败'
    logLoading.value = false
  }
}

const closeLogDialog = () => {
  showLogDialog.value = false
  logContent.value = ''
  currentLogId.value = null
}

const downloadLog = () => {
  if (!logContent.value) return
  
  // 创建 Blob 对象
  const blob = new Blob([logContent.value], { type: 'text/plain;charset=utf-8' })
  
  // 创建下载链接
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `train${currentLogId.value}_log.txt`
  
  // 触发下载
  document.body.appendChild(link)
  link.click()
  
  // 清理
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

const viewDatasets = async (trainingId) => {
  currentDatasetTrainingId.value = trainingId
  datasetError.value = ''
  datasetRecords.value = []
  showDatasetDialog.value = true
  datasetLoading.value = true
  
  try {
    const response = await axios.get(`/api/render/training/${trainingId}`)
    datasetRecords.value = response.data.data
    datasetLoading.value = false
  } catch (error) {
    console.error('加载数据集信息失败:', error)
    datasetError.value = error.response?.data?.error || '加载数据集信息失败'
    datasetLoading.value = false
  }
}

const closeDatasetDialog = () => {
  showDatasetDialog.value = false
  datasetRecords.value = []
  currentDatasetTrainingId.value = null
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

const drawCharts = () => {
  console.log('drawCharts 被调用')
  console.log('monitorData.value:', monitorData.value)
  
  if (monitorData.value.length === 0) {
    console.log('没有数据，退出')
    return
  }
  
  const labels = monitorData.value.map(d => d.timestamp)
  console.log('时间标签:', labels)
  
  if (cpuChart.value) {
    console.log('绘制 CPU 图表')
    if (cpuChartInstance) cpuChartInstance.destroy()
    const cpuData = monitorData.value.map(d => parseFloat(d.cpu_usage_total_seconds))
    console.log('CPU 数据:', cpuData)
    
    cpuChartInstance = new Chart(cpuChart.value, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'CPU 使用 (秒)',
          data: cpuData,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true } }
      }
    })
    console.log('CPU 图表创建完成')
  } else {
    console.log('cpuChart ref 不存在')
  }
  
  if (gpuChart.value) {
    console.log('绘制 GPU 图表')
    if (gpuChartInstance) gpuChartInstance.destroy()
    const gpuData = monitorData.value.map(d => parseFloat(d['gpu_utilization_total(%)']))
    console.log('GPU 数据:', gpuData)
    
    gpuChartInstance = new Chart(gpuChart.value, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'GPU 利用率 (%)',
          data: gpuData,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true } },
        scales: { y: { beginAtZero: true, max: 100 } }
      }
    })
    console.log('GPU 图表创建完成')
  } else {
    console.log('gpuChart ref 不存在')
  }
  
  if (memoryChart.value) {
    console.log('绘制内存图表')
    if (memoryChartInstance) memoryChartInstance.destroy()
    const gpuMemData = monitorData.value.map(d => parseFloat(d.gpu_memory_total_mb))
    const sysMemData = monitorData.value.map(d => parseFloat(d.memory_usage_total_mb))
    console.log('GPU 内存数据:', gpuMemData)
    console.log('系统内存数据:', sysMemData)
    
    memoryChartInstance = new Chart(memoryChart.value, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'GPU 内存 (MB)',
            data: gpuMemData,
            borderColor: 'rgb(153, 102, 255)',
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            tension: 0.1
          },
          {
            label: '系统内存 (MB)',
            data: sysMemData,
            borderColor: 'rgb(255, 159, 64)',
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            tension: 0.1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true } }
      }
    })
    console.log('内存图表创建完成')
  } else {
    console.log('memoryChart ref 不存在')
  }
}

const deleteMonitorRecord = (trainingId) => {
  const stored = localStorage.getItem('monitorRecords')
  if (!stored) return
  
  let monitorRecords = JSON.parse(stored)
  monitorRecords = monitorRecords.filter(r => r.trainingId !== trainingId)
  
  localStorage.setItem('monitorRecords', JSON.stringify(monitorRecords))
  window.dispatchEvent(new StorageEvent('storage', {
    key: 'monitorRecords',
    newValue: JSON.stringify(monitorRecords)
  }))
}

onMounted(() => {
  // 加载训练记录
  loadTrainingRecords()
  
  // 连接WebSocket
  socket = io('http://localhost:8000')

  socket.on('connect', () => {
    console.log('WebSocket已连接')
  })

  socket.on('training_log', (data) => {
    console.log('收到日志:', data)
    // 使用消息中的 training_id，而不是全局变量
    const trainingId = data.training_id
    if (trainingId && activeTrainingIds.has(trainingId)) {
      const record = trainingRecords.value.find(r => r.training_id === trainingId)
      if (record) {
        if (!record.logs) {
          record.logs = []
        }
        record.logs.push(data.message)
        // 不自动展开日志，保持当前状态
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
          
          // 只刷新这一条记录，不影响其他记录
          await refreshSingleRecord(trainingId)
        } else {
          message.value = `训练 ${trainingId} 失败：${data.message}`
          messageType.value = 'error'
        }
      }
      // 从活跃集合中移除
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
  background: #764ba2 100%;
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
  background: #667eea 100%;
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
  border-color: #9c27b0;
}

.filter-select:focus {
  outline: none;
  border-color: #9c27b0;
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
  gap: 1rem;
  flex-wrap: nowrap;
}

.monitor-btn,
.log-btn,
.dataset-btn,
.start-btn,
.refresh-btn,
.delete-btn {
  padding: 0.4rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.3s;
  white-space: nowrap;
  outline: none;
}

.monitor-btn:focus,
.log-btn:focus,
.dataset-btn:focus,
.start-btn:focus,
.refresh-btn:focus,
.delete-btn:focus {
  outline: none;
}

.monitor-btn {
  background: #3498db;
  color: white;
}

.monitor-btn:hover {
  background: #2980b9;
}

.log-btn {
  background: #f39c12;
  color: white;
}

.log-btn:hover {
  background: #e67e22;
}

.dataset-btn {
  background: #16a085;
  color: white;
}

.dataset-btn:hover {
  background: #138d75;
}

.start-btn {
  background: #42b983;
  color: white;
}

.start-btn:hover:not(:disabled) {
  background: #359268;
}

.refresh-btn {
  background: #3498db;
  color: white;
}

.refresh-btn:hover:not(:disabled) {
  background: #2980b9;
}

.delete-btn {
  background: #e74c3c;
  color: white;
}

.delete-btn:hover:not(:disabled) {
  background: #c0392b;
}

.completed-badge {
  padding: 0.5rem 1.5rem;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: bold;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
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

.result-section {
  margin-top: 1rem;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

thead {
  background: #f5f5f5;
}

th,
td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
  font-size: 0.9rem;
}

th {
  font-weight: bold;
  color: #555;
}

tbody tr:hover {
  background: #f9f9f9;
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
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.dialog-header h3 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.download-btn {
  padding: 0.5rem 1rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.3s;
}

.download-btn:hover {
  background: #2980b9;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.dialog-body {
  padding: 2rem;
  min-height: 200px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #eee;
}

.cancel-btn,
.confirm-btn {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.cancel-btn {
  background: #e0e0e0;
  color: #333;
}

.cancel-btn:hover {
  background: #d0d0d0;
}

.confirm-btn {
  background: #9c27b0;
  color: white;
}

.confirm-btn:hover {
  background: #7b1fa2;
}

.monitor-dialog {
  max-width: 1200px;
  width: 95%;
}

.monitor-dialog .dialog-body {
  padding: 2rem;
  min-height: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.chart-item {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.chart-item h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
}

.chart-item canvas {
  width: 100% !important;
  height: 300px !important;
}

.loading,
.no-data {
  text-align: center;
  padding: 3rem;
  color: #666;
  font-size: 1.1rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #666;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #9c27b0;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.log-dialog {
  max-width: 1000px;
  width: 90%;
}

.log-dialog .dialog-body {
  padding: 0;
  max-height: 70vh;
  overflow-y: auto;
}

.log-content {
  background: #1e1e1e;
  padding: 1.5rem;
  min-height: 500px;
}

.log-content pre {
  margin: 0;
  color: #d4d4d4;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.5;
}

.error-message {
  text-align: center;
  padding: 3rem;
  color: #e74c3c;
  font-size: 1.1rem;
}

.create-dialog {
  max-width: 700px;
  width: 90%;
}

.create-dialog .dialog-body {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

.render-selection h4 {
  margin: 0 0 1rem 0;
  color: #333;
}

.render-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.render-item {
  border: 1px solid #ddd;
  border-radius: 4px;
  transition: all 0.3s;
}

.render-item:hover {
  border-color: #9c27b0;
  background: #f9f9f9;
}

.render-checkbox {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  cursor: pointer;
  gap: 1rem;
}

.render-checkbox input[type="checkbox"] {
  margin-top: 0.25rem;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.render-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #555;
}

.dataset-dialog {
  max-width: 700px;
  width: 90%;
}

.dataset-dialog .dialog-body {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

.dataset-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dataset-item {
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.dataset-field {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #555;
}

.dataset-field:last-child {
  margin-bottom: 0;
}
</style>

