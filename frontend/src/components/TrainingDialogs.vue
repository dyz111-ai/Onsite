<template>
  <!-- 新增训练弹窗 -->
  <div v-if="createDialog.show" class="dialog-overlay" @click="$emit('close-create')">
    <div class="dialog-content create-dialog" @click.stop>
      <div class="dialog-header">
        <h3>新增训练</h3>
        <button class="close-btn" @click="$emit('close-create')">×</button>
      </div>
      <div class="dialog-body">
        <div v-if="createDialog.loading" class="loading">加载数据集中...</div>
        <div v-else-if="createDialog.renders.length === 0" class="no-data">暂无可用数据集</div>
        <div v-else class="render-selection">
          <h4>选择数据集</h4>
          <div class="render-list">
            <div v-for="render in createDialog.renders" :key="render.render_id" class="render-item">
              <label class="render-checkbox">
                <input 
                  type="checkbox" 
                  :value="render.render_id" 
                  v-model="createDialog.selectedIds"
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
        <button @click="$emit('close-create')" class="cancel-btn" :disabled="createDialog.creating">取消</button>
        <button @click="$emit('confirm-create', createDialog.selectedIds)" class="confirm-btn" :disabled="createDialog.selectedIds.length === 0 || createDialog.creating">
          <span v-if="createDialog.creating">创建中...</span>
          <span v-else>确定 (已选 {{ createDialog.selectedIds.length }})</span>
        </button>
      </div>
    </div>
  </div>

  <!-- 监控图表弹窗 -->
  <div v-if="monitorDialog.show" class="dialog-overlay" @click="$emit('close-monitor')">
    <div class="dialog-content monitor-dialog" @click.stop>
      <div class="dialog-header">
        <h3>训练监控 - ID: {{ monitorDialog.trainingId }}</h3>
        <button class="close-btn" @click="$emit('close-monitor')">×</button>
      </div>
      <div class="dialog-body">
        <div v-if="monitorDialog.loading" class="loading">加载中...</div>
        <div v-else-if="monitorDialog.error" class="error-message">{{ monitorDialog.error }}</div>
        <div v-else-if="monitorDialog.data.length === 0" class="no-data">暂无监控数据</div>
        <div v-else>
          <!-- 导航栏 -->
          <div class="monitor-nav">
            <button 
              :class="['nav-btn', { active: monitorView === 'charts' }]" 
              @click="monitorView = 'charts'"
            >
              图表变化
            </button>
            <button 
              :class="['nav-btn', { active: monitorView === 'data' }]" 
              @click="monitorView = 'data'"
            >
              监控数值
            </button>
          </div>

          <!-- 图表视图 -->
          <div v-if="monitorView === 'charts'" class="charts-container">
            <div class="chart-item">
              <h4>CPU 使用增量 (秒)</h4>
              <canvas ref="cpuChart"></canvas>
            </div>
            <div class="chart-item">
              <h4>GPU 利用率 (%)</h4>
              <canvas ref="gpuChart"></canvas>
            </div>
            <div class="chart-item">
              <h4>内存使用 (MB)</h4>
              <canvas ref="memoryChart"></canvas>
            </div>
          </div>

          <!-- 数据表格视图 -->
          <div v-if="monitorView === 'data'" class="data-table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>时间戳</th>
                  <th>训练时长(秒)</th>
                  <th>CPU使用(秒)</th>
                  <th>GPU利用率(%)</th>
                  <th>GPU显存(MB)</th>
                  <th>系统内存(MB)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in monitorDialog.data" :key="index">
                  <td>{{ row.timestamp }}</td>
                  <td>{{ parseFloat(row.training_time_seconds).toFixed(2) }}</td>
                  <td>{{ parseFloat(row.cpu_usage_total_seconds).toFixed(2) }}</td>
                  <td>{{ parseFloat(row['gpu_utilization_total(%)']).toFixed(2) }}</td>
                  <td>{{ parseFloat(row.gpu_memory_total_mb).toFixed(2) }}</td>
                  <td>{{ parseFloat(row.memory_usage_total_mb).toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 训练日志弹窗 -->
  <div v-if="logDialog.show" class="dialog-overlay" @click="$emit('close-log')">
    <div class="dialog-content log-dialog" @click.stop>
      <div class="dialog-header">
        <h3>训练日志 - ID: {{ logDialog.trainingId }}</h3>
        <div class="header-actions">
          <button v-if="!logDialog.loading && !logDialog.error" @click="$emit('download-log', logDialog.content)" class="download-btn">
            下载日志
          </button>
          <button class="close-btn" @click="$emit('close-log')">×</button>
        </div>
      </div>
      <div class="dialog-body">
        <div v-if="logDialog.loading" class="loading">加载中...</div>
        <div v-else-if="logDialog.error" class="error-message">{{ logDialog.error }}</div>
        <div v-else class="log-content">
          <pre>{{ logDialog.content }}</pre>
        </div>
      </div>
    </div>
  </div>

  <!-- 数据集信息弹窗 -->
  <div v-if="datasetDialog.show" class="dialog-overlay" @click="$emit('close-dataset')">
    <div class="dialog-content dataset-dialog" @click.stop>
      <div class="dialog-header">
        <h3>数据集信息 - 训练ID: {{ datasetDialog.trainingId }}</h3>
        <button class="close-btn" @click="$emit('close-dataset')">×</button>
      </div>
      <div class="dialog-body">
        <div v-if="datasetDialog.loading" class="loading">加载中...</div>
        <div v-else-if="datasetDialog.error" class="error-message">{{ datasetDialog.error }}</div>
        <div v-else-if="datasetDialog.datasets.length === 0" class="no-data">该训练未关联数据集</div>
        <div v-else class="dataset-list">
          <div v-for="dataset in datasetDialog.datasets" :key="dataset.render_id" class="dataset-item">
            <div class="dataset-field"><strong>名称：</strong>{{ dataset.name || '未命名' }}</div>
            <div class="dataset-field"><strong>状态：</strong>{{ dataset.status }}</div>
            <div class="dataset-field"><strong>创建时间：</strong>{{ dataset.created_time }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

// 注册 Chart.js 所有组件
Chart.register(...registerables)

const props = defineProps({
  createDialog: {
    type: Object,
    default: () => ({ show: false, loading: false, renders: [], selectedIds: [] })
  },
  monitorDialog: {
    type: Object,
    default: () => ({ show: false, loading: false, error: '', trainingId: null, data: [] })
  },
  logDialog: {
    type: Object,
    default: () => ({ show: false, loading: false, error: '', trainingId: null, content: '' })
  },
  datasetDialog: {
    type: Object,
    default: () => ({ show: false, loading: false, error: '', trainingId: null, datasets: [] })
  }
})

defineEmits(['close-create', 'confirm-create', 'close-monitor', 'close-log', 'download-log', 'close-dataset'])

const monitorView = ref('charts') // 'charts' 或 'data'
const cpuChart = ref(null)
const gpuChart = ref(null)
const memoryChart = ref(null)
let cpuChartInstance = null
let gpuChartInstance = null
let memoryChartInstance = null

// 绘制监控图表
const drawMonitorCharts = () => {
  if (props.monitorDialog.data.length === 0) return
  
  // 处理标签：只显示时分秒，每5个显示一次
  const labels = props.monitorDialog.data.map((d, index) => {
    if (index % 5 === 0) {
      // 提取时分秒部分 (HH:MM:SS)
      const timestamp = d.timestamp
      if (timestamp && timestamp.includes(' ')) {
        return timestamp.split(' ')[1] // 只取时间部分
      }
      return timestamp
    }
    return '' // 其他位置不显示标签
  })
  
  if (cpuChart.value) {
    if (cpuChartInstance) cpuChartInstance.destroy()
    
    // 计算CPU使用增量（当前时间点 - 上一时间点）
    const cpuData = props.monitorDialog.data.map((d, index) => {
      if (index === 0) {
        return 0 // 第一个数据点没有上一个时间点，设为0
      }
      const current = parseFloat(d.cpu_usage_total_seconds)
      const previous = parseFloat(props.monitorDialog.data[index - 1].cpu_usage_total_seconds)
      return Math.max(0, current - previous) // 确保不为负数
    })
    
    cpuChartInstance = new Chart(cpuChart.value, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'CPU 使用增量 (秒)',
          data: cpuData,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true } },
        scales: {
          x: {
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          }
        }
      }
    })
  }
  
  if (gpuChart.value) {
    if (gpuChartInstance) gpuChartInstance.destroy()
    const gpuData = props.monitorDialog.data.map(d => parseFloat(d['gpu_utilization_total(%)']))
    
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
        scales: { 
          x: {
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          },
          y: { beginAtZero: true, max: 100 } 
        }
      }
    })
  }
  
  if (memoryChart.value) {
    if (memoryChartInstance) memoryChartInstance.destroy()
    const gpuMemData = props.monitorDialog.data.map(d => parseFloat(d.gpu_memory_total_mb))
    const sysMemData = props.monitorDialog.data.map(d => parseFloat(d.memory_usage_total_mb))
    
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
        plugins: { legend: { display: true } },
        scales: {
          x: {
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          }
        }
      }
    })
  }
}

// 监听监控弹窗数据变化
watch(() => props.monitorDialog.data, async (newData) => {
  if (newData.length > 0 && props.monitorDialog.show && monitorView.value === 'charts') {
    await nextTick()
    await nextTick()
    setTimeout(() => {
      drawMonitorCharts()
    }, 100)
  }
}, { deep: true })

// 监听监控弹窗关闭
watch(() => props.monitorDialog.show, (newVal) => {
  if (!newVal) {
    if (cpuChartInstance) cpuChartInstance.destroy()
    if (gpuChartInstance) gpuChartInstance.destroy()
    if (memoryChartInstance) memoryChartInstance.destroy()
    cpuChartInstance = null
    gpuChartInstance = null
    memoryChartInstance = null
    monitorView.value = 'charts' // 重置为图表视图
  }
})

// 监听视图切换
watch(monitorView, async (newView) => {
  if (newView === 'charts' && props.monitorDialog.data.length > 0) {
    await nextTick()
    await nextTick()
    setTimeout(() => {
      drawMonitorCharts()
    }, 100)
  }
})
</script>

<style scoped>
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
  max-height: 90vh;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.monitor-dialog {
  max-width: 1200px;
  width: 95%;
}

.log-dialog {
  max-width: 1000px;
  width: 95%;
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
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: opacity 0.3s;
}

.download-btn:hover {
  opacity: 0.85;
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
  overflow-y: auto;
  flex: 1;
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

.confirm-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading,
.error-message,
.no-data {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error-message {
  color: #c62828;
}

.render-selection h4 {
  margin: 0 0 1rem 0;
  color: #555;
}

.render-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 400px;
  overflow-y: auto;
}

.render-item {
  border: 1px solid #ddd;
  border-radius: 4px;
  transition: border-color 0.3s;
}

.render-item:hover {
  border-color: #9c27b0;
}

.render-checkbox {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  cursor: pointer;
}

.render-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.render-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.9rem;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.chart-item {
  background: #fafafa;
  padding: 1.5rem;
  border-radius: 6px;
}

.chart-item h4 {
  margin: 0 0 1rem 0;
  color: #555;
}

.chart-item canvas {
  max-height: 300px;
}

.log-content {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 1rem;
  border-radius: 4px;
  max-height: 600px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.log-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.dataset-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dataset-item {
  background: #fafafa;
  padding: 1rem;
  border-radius: 4px;
  border-left: 4px solid #42b983;
}

.dataset-field {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #555;
}

.dataset-field:last-child {
  margin-bottom: 0;
}

.monitor-nav {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #eee;
}

.nav-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  color: #666;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
}

.nav-btn:hover {
  color: #333;
}

.nav-btn.active {
  color: #007bff;
  border-bottom-color: #007bff;
  font-weight: 600;
}

.data-table-container {
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table thead {
  position: sticky;
  top: 0;
  background: #f5f5f5;
  z-index: 1;
}

.data-table th {
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #ddd;
  white-space: nowrap;
}

.data-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #eee;
  white-space: nowrap;
}

.data-table tbody tr:hover {
  background: #f9f9f9;
}
</style>
