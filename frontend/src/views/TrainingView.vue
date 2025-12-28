<template>
  <div class="training-view">
    <h2>训练</h2>
    <div class="control-panel">
      <button @click="showCreateDialog" class="create-btn">
        新增训练
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
    <div v-else-if="trainingRecords.length > 0" class="records-section">
      <h3>训练记录</h3>
      <div class="records-container">
        <div class="records-list">
          <div v-for="record in trainingRecords" :key="record.id" class="record-card">
            <div class="record-header">
              <div class="record-info">
                <div class="record-field">
                  <strong>训练ID：</strong>{{ record.training_id }}
                </div>
                <div class="record-field">
                  <strong>创建时间：</strong>{{ record.createdAt }}
                </div>
                <div class="record-field">
                  <strong>状态：</strong>{{ record.status }}
                </div>
                <div class="record-field">
                  <strong>训练成本：</strong>{{ record.train_cost }}
                </div>
                <div class="record-field">
                  <strong>测试分数：</strong>{{ record.test_score }}
                </div>
              </div>
              <div class="record-actions">
                <button @click="viewMonitor(record.training_id)" class="monitor-btn">
                  查看监控
                </button>
                <button @click="deleteRecord(record.id)" class="delete-btn">
                  删除
                </button>
              </div>
            </div>
            
            <!-- 训练日志 -->
            <div v-if="record.logs && record.logs.length > 0" class="log-section">
              <div class="log-header">
                <h4>执行日志</h4>
                <button @click="toggleLogs(record.training_id)" class="toggle-logs-btn">
                  {{ record.showLogs ? '隐藏日志' : '显示日志' }}
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

    <!-- 新增训练弹窗 -->
    <div v-if="showDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>新增训练</h3>
          <button class="close-btn" @click="closeDialog">×</button>
        </div>
        <div class="dialog-body">
          <!-- 弹窗内容留白 -->
        </div>
        <div class="dialog-footer">
          <button @click="closeDialog" class="cancel-btn">取消</button>
          <button @click="createTraining" class="confirm-btn">确定</button>
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
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
let socket = null
let currentTrainingId = null

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
    // 为每条记录添加日志数组和显示状态
    trainingRecords.value = (result.data || []).map(record => ({
      ...record,
      logs: record.logs || [],
      showLogs: false
    }))
  } catch (error) {
    message.value = '加载训练记录失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
    trainingRecords.value = []
  } finally {
    loading.value = false
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

const showCreateDialog = () => {
  showDialog.value = true
}

const closeDialog = () => {
  showDialog.value = false
}

const createTraining = async () => {
  try {
    // 创建训练记录
    const result = await createTrainingRecord()
    const trainingId = result.data.training_id
    
    // 设置当前训练ID
    currentTrainingId = trainingId
    
    // 重新加载记录列表
    await loadTrainingRecords()
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
      currentTrainingId = null
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
    if (currentTrainingId) {
      const record = trainingRecords.value.find(r => r.training_id === currentTrainingId)
      if (record) {
        if (!record.logs) {
          record.logs = []
        }
        record.logs.push(data.message)
        // 自动展开日志
        record.showLogs = true
        scrollToBottom(currentTrainingId)
      }
    }
  })

  socket.on('training_complete', async (data) => {
    console.log('训练完成:', data)
    if (currentTrainingId) {
      const record = trainingRecords.value.find(r => r.training_id === currentTrainingId)
      if (record) {
        if (data.status === 'success') {
          message.value = `训练 ${currentTrainingId} 完成！`
          messageType.value = 'success'
          
          // 重新加载训练记录以获取更新后的成本
          await loadTrainingRecords()
        } else {
          message.value = `训练 ${currentTrainingId} 失败：${data.message}`
          messageType.value = 'error'
        }
      }
      currentTrainingId = null
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

.control-panel {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.create-btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
  background: #9c27b0;
  color: white;
}

.create-btn:hover {
  background: #7b1fa2;
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
}

.record-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: nowrap;
}

.monitor-btn,
.start-btn,
.refresh-btn,
.delete-btn {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.3s;
}

.monitor-btn {
  background: #3498db;
  color: white;
}

.monitor-btn:hover {
  background: #2980b9;
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
</style>

