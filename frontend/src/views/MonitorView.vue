<template>
  <div class="monitor-view">
    <h2>监控</h2>
    
    <div v-if="monitorRecords.length === 0" class="empty-state">
      <p>暂无监控记录</p>
    </div>

    <div v-else class="monitor-container">
      <div class="monitor-list">
        <div v-for="record in monitorRecords" :key="record.id" class="monitor-card">
          <div class="monitor-header">
            <div class="monitor-info">
              <div class="monitor-id">
                <strong>训练ID：</strong>{{ record.trainingId }}
              </div>
              <div class="monitor-time">
                <strong>创建时间：</strong>{{ record.createdAt }}
              </div>
              <div class="monitor-status" :class="'status-' + record.status">
                <strong>状态：</strong>{{ getStatusText(record.status) }}
              </div>
            </div>
            <div v-if="record.status === 'completed' && record.data && record.data.length > 0">
              <button @click="showChartDialog(record)" class="view-chart-btn">
                查看资源使用情况
              </button>
            </div>
          </div>

          <!-- 未完成状态的提示 -->
          <div v-if="record.status !== 'completed'" class="pending-message">
            <p>{{ record.status === 'running' ? '训练进行中，请等待完成后查看监控数据' : '训练未开始或已失败' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表弹窗 -->
    <div v-if="dialogVisible" class="chart-dialog-overlay" @click="closeDialog">
      <div class="chart-dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>资源使用情况 - {{ currentRecord?.trainingId }}</h3>
          <button class="close-btn" @click="closeDialog">×</button>
        </div>
        <div class="dialog-body">
          <!-- 图表展示 -->
          <div class="charts-container">
            <div class="chart-wrapper">
              <h5>CPU使用率</h5>
              <canvas ref="cpuChartRef"></canvas>
            </div>
            <div class="chart-wrapper">
              <h5>GPU利用率</h5>
              <canvas ref="gpuChartRef"></canvas>
            </div>
            <div class="chart-wrapper">
              <h5>内存使用</h5>
              <canvas ref="memoryChartRef"></canvas>
            </div>
          </div>

          <!-- 数据表格 -->
          <details class="data-table-details">
            <summary>查看详细数据</summary>
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>时间戳</th>
                    <th>训练时间(秒)</th>
                    <th>CPU使用(秒)</th>
                    <th>GPU利用率(%)</th>
                    <th>GPU内存(MB)</th>
                    <th>内存使用(MB)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in currentRecord?.data" :key="index">
                    <td>{{ row.timestamp }}</td>
                    <td>{{ row.training_time_seconds }}</td>
                    <td>{{ row.cpu_usage_total_seconds }}</td>
                    <td>{{ row['gpu_utilization_total(%)'] }}</td>
                    <td>{{ row.gpu_memory_total_mb }}</td>
                    <td>{{ row.memory_usage_total_mb }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </details>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const monitorRecords = ref([])
const dialogVisible = ref(false)
const currentRecord = ref(null)
const cpuChartRef = ref(null)
const gpuChartRef = ref(null)
const memoryChartRef = ref(null)
let cpuChart = null
let gpuChart = null
let memoryChart = null

const getStatusText = (status) => {
  const statusMap = {
    'pending': '等待中',
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || status
}

const showChartDialog = (record) => {
  currentRecord.value = record
  dialogVisible.value = true
  nextTick(() => {
    createCharts()
  })
}

const closeDialog = () => {
  dialogVisible.value = false
  destroyCharts()
  currentRecord.value = null
}

const destroyCharts = () => {
  if (cpuChart) {
    cpuChart.destroy()
    cpuChart = null
  }
  if (gpuChart) {
    gpuChart.destroy()
    gpuChart = null
  }
  if (memoryChart) {
    memoryChart.destroy()
    memoryChart = null
  }
}

const createCharts = () => {
  if (!currentRecord.value || !currentRecord.value.data) return

  const data = currentRecord.value.data
  const labels = data.map(d => d.timestamp)

  // CPU使用率图表
  if (cpuChartRef.value) {
    cpuChart = new Chart(cpuChartRef.value, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'CPU使用(秒)',
          data: data.map(d => parseFloat(d.cpu_usage_total_seconds)),
          borderColor: '#3498db',
          backgroundColor: 'rgba(52, 152, 219, 0.1)',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    })
  }

  // GPU利用率图表
  if (gpuChartRef.value) {
    gpuChart = new Chart(gpuChartRef.value, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'GPU利用率(%)',
          data: data.map(d => parseFloat(d['gpu_utilization_total(%)'])),
          borderColor: '#e74c3c',
          backgroundColor: 'rgba(231, 76, 60, 0.1)',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    })
  }

  // 内存使用图表
  if (memoryChartRef.value) {
    memoryChart = new Chart(memoryChartRef.value, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'GPU内存(MB)',
            data: data.map(d => parseFloat(d.gpu_memory_total_mb)),
            borderColor: '#9b59b6',
            backgroundColor: 'rgba(155, 89, 182, 0.1)',
            tension: 0.4
          },
          {
            label: '系统内存(MB)',
            data: data.map(d => parseFloat(d.memory_usage_total_mb)),
            borderColor: '#2ecc71',
            backgroundColor: 'rgba(46, 204, 113, 0.1)',
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    })
  }
}

const loadMonitorRecords = () => {
  const stored = localStorage.getItem('monitorRecords')
  if (stored) {
    monitorRecords.value = JSON.parse(stored)
  }
}

let refreshInterval = null

onMounted(() => {
  loadMonitorRecords()
  
  window.addEventListener('storage', (e) => {
    if (e.key === 'monitorRecords') {
      loadMonitorRecords()
    }
  })
  
  // 定时刷新
  refreshInterval = setInterval(() => {
    loadMonitorRecords()
  }, 3000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  destroyCharts()
})
</script>

<style scoped>
.monitor-view {
  padding: 2rem;
  min-height: 100vh;
  width: 100%;
}

h2 {
  color: #333;
  margin-bottom: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #999;
  font-size: 1.1rem;
}

.monitor-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 1.5rem;
}

.monitor-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.monitor-card {
  background: #fafafa;
  padding: 1.5rem;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  border-left: 4px solid #2196f3;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.monitor-info {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.monitor-id,
.monitor-time,
.monitor-status {
  color: #555;
}

.monitor-status {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.status-pending {
  background: #fff3e0;
  color: #f57c00;
}

.status-running {
  background: #e3f2fd;
  color: #1976d2;
}

.status-completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-failed {
  background: #ffebee;
  color: #c62828;
}

.view-chart-btn {
  padding: 0.5rem 1.5rem;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.view-chart-btn:hover {
  background: #1976d2;
}

.pending-message {
  margin-top: 1rem;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 4px;
  text-align: center;
  color: #666;
}

/* 弹窗样式 */
.chart-dialog-overlay {
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

.chart-dialog-content {
  background: white;
  border-radius: 8px;
  width: 95%;
  max-width: 1400px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
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
}

h5 {
  color: #666;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.chart-wrapper {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  height: 350px;
}

.chart-wrapper canvas {
  max-height: 300px;
}

.data-table-details {
  margin-top: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0.5rem;
}

.data-table-details summary {
  cursor: pointer;
  padding: 0.5rem;
  font-weight: bold;
  color: #555;
  user-select: none;
}

.data-table-details summary:hover {
  background: #f5f5f5;
}

.table-container {
  overflow-x: auto;
  margin-top: 1rem;
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
</style>
