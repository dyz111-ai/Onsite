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

    <!-- 训练记录列表 -->
    <div v-if="trainingRecords.length > 0" class="records-section">
      <h3>训练记录</h3>
      <div class="records-container">
        <div class="records-list">
          <div v-for="record in trainingRecords" :key="record.id" class="record-card">
            <div class="record-header">
              <div class="record-info">
                <div class="record-id">
                  <strong>训练ID：</strong>{{ record.id }}
                </div>
                <div class="record-time">
                  <strong>创建时间：</strong>{{ record.createdAt }}
                </div>
              </div>
              <div class="record-actions">
                <button 
                  v-if="record.status !== 'completed'"
                  @click="handleStartTraining(record.id)" 
                  :disabled="record.loading || record.status === 'running'" 
                  class="start-btn">
                  {{ record.loading ? '训练中...' : record.status === 'running' ? '运行中' : '开始训练' }}
                </button>
                <span v-else class="completed-badge">已完成</span>

                <button @click="deleteRecord(record.id)" :disabled="record.loading" class="delete-btn">
                  删除
                </button>
              </div>
            </div>
            
            <!-- 该记录的日志输出 -->
            <div v-if="record.logs && record.logs.length > 0" class="log-section">
              <div class="log-header">
                <h4>执行日志</h4>
                <button @click="toggleLogs(record.id)" class="toggle-logs-btn">
                  {{ record.showLogs ? '隐藏日志' : '显示日志' }}
                </button>
              </div>
              <div v-if="record.showLogs" class="log-container" :ref="el => setLogRef(record.id, el)">
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { startTraining, getTrainingResult } from '../api/training'
import { getTrainingRecords, createTrainingRecord, updateTrainingRecord, deleteTrainingRecord } from '../api/trainingRecords'
import { io } from 'socket.io-client'

const message = ref('')
const messageType = ref('info')
const showDialog = ref(false)
const trainingRecords = ref([])
const logRefs = ref({})
let socket = null
let currentTrainingId = null

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
const toggleLogs = (recordId) => {
  const record = trainingRecords.value.find(r => r.id === recordId)
  if (record) {
    record.showLogs = !record.showLogs
    if (record.showLogs) {
      // 显示日志后滚动到底部
      scrollToBottom(recordId)
    }
  }
}

// 从服务器加载训练记录
const loadTrainingRecords = async () => {
  try {
    const result = await getTrainingRecords()
    // 为每个记录添加运行时状态
    trainingRecords.value = (result.data || []).map(record => ({
      ...record,
      loading: false,  // 运行时状态，不保存到 JSON
      showLogs: false  // 默认不显示日志
    }))
  } catch (error) {
    message.value = '加载训练记录失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
    trainingRecords.value = []
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
  // 生成训练记录
  const newRecord = {
    id: 'TRAIN-' + Date.now(),
    createdAt: new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }),
    logs: [],
    csvData: [],
    status: 'pending'  // 添加状态字段：pending, running, completed, failed
  }
  
  try {
    await createTrainingRecord(newRecord)
    // 重新加载记录列表
    await loadTrainingRecords()
    closeDialog()
    
    // 同时在监控面板创建监控记录
    createMonitorRecord(newRecord.id, newRecord.createdAt)
    
    message.value = '训练记录已创建'
    messageType.value = 'success'
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
    // 重新加载记录列表
    await loadTrainingRecords()
    
    // 同时删除对应的监控记录
    deleteMonitorRecord(recordId)
    
    message.value = '训练记录已删除'
    messageType.value = 'success'
  } catch (error) {
    message.value = '删除失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
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
    if (currentTrainingId) {
      const record = trainingRecords.value.find(r => r.id === currentTrainingId)
      if (record) {
        record.logs.push(data.message)
        scrollToBottom(currentTrainingId)
        // 保存日志更新到服务器（节流，避免频繁保存）
        if (record.logs.length % 10 === 0) {
          saveRecordUpdate(currentTrainingId, { logs: record.logs })
        }
      }
    }
  })

  socket.on('training_complete', async (data) => {
    if (currentTrainingId) {
      const record = trainingRecords.value.find(r => r.id === currentTrainingId)
      if (record) {
        record.loading = false
        
        if (data.status === 'success') {
          // 训练成功，自动加载CSV结果
          message.value = '训练完成！正在加载结果...'          
          messageType.value = 'success'
          
          try {
            // 加载CSV数据
            const result = await getTrainingResult()
            record.csvData = result.data
            
            // 更新状态为completed，但不保存csvData到JSON
            await saveRecordUpdate(currentTrainingId, { 
              status: 'completed',
              logs: record.logs
            })
            
            // 更新监控记录
            updateMonitorStatus(currentTrainingId, 'completed', result.data)
            
            message.value = '训练完成！已自动加载监控数据'
            messageType.value = 'success'
          } catch (error) {
            message.value = '训练完成，但加载结果失败：' + (error.response?.data?.error || error.message)
            messageType.value = 'error'
            await saveRecordUpdate(currentTrainingId, { status: 'completed', logs: record.logs })
          }
        } else {
          // 训练失败
          message.value = '训练失败：' + data.message
          messageType.value = 'error'
          await saveRecordUpdate(currentTrainingId, { status: 'failed', logs: record.logs })
          updateMonitorStatus(currentTrainingId, 'failed')
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
}

.record-id,
.record-time {
  color: #555;
}

.record-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: nowrap;
}

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
</style>

