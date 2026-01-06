<template>
  <div class="evaluation-view">
    <h2>测试评估</h2>
    
    <div class="filter-group">
      <input 
        v-model="searchId" 
        type="text" 
        placeholder="搜索训练ID" 
        class="search-input"
      />
      
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
      
      <select v-model="sortBy" class="filter-select">
        <option value="">默认排序</option>
        <option value="render_cost">渲染成本</option>
        <option value="train_cost">训练成本</option>
        <option value="test_score">测试分数</option>
        <option value="total_score">总分</option>
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
                <button 
                  v-if="record.status === 'Trained'"
                  @click="startTest(record.training_id)" 
                  class="action-btn test-btn"
                >
                  生成测试
                </button>
                <button 
                  v-if="record.status === 'Tested'"
                  @click="viewResult(record.training_id)" 
                  class="action-btn result-btn"
                >
                  查看结果
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 测试确认弹窗 -->
    <div v-if="showTestDialog" class="dialog-overlay" @click="closeTestDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>确认</h3>
          <button @click="closeTestDialog" class="close-btn">&times;</button>
        </div>
        
        <div class="dialog-body">
          <p>确定要生成测试训练ID {{ currentTestingId }} 吗？</p>
        </div>
        
        <div class="dialog-footer">
          <button @click="closeTestDialog" class="cancel-btn">取消</button>
          <button @click="confirmTest" :disabled="testing" class="confirm-btn">
            {{ testing ? '加载中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 查看结果弹窗 -->
    <div v-if="showResultDialog" class="dialog-overlay" @click="closeResultDialog">
      <div class="dialog-content result-dialog" @click.stop>
        <div class="dialog-header">
          <h3>测试结果 - 训练ID {{ currentResultId }}</h3>
          <button @click="closeResultDialog" class="close-btn">&times;</button>
        </div>
        
        <div class="dialog-body">
          <div v-if="loadingResult" class="loading-container">
            <div class="loading-spinner"></div>
            <p>加载结果中...</p>
          </div>
          
          <div v-else-if="parsedResults" class="results-container">
            <!-- 总体指标卡片 -->
            <div class="summary-section">
              <h4>总体评估指标</h4>
              <div class="metrics-grid">
                <div class="metric-card" v-if="parsedResults.summary.NDS !== undefined">
                  <div class="metric-label">NDS (驾驶检测分数)</div>
                  <div class="metric-value">{{ parsedResults.summary.NDS.toFixed(4) }}</div>
                </div>
                <div class="metric-card" v-if="parsedResults.summary.mAP !== undefined">
                  <div class="metric-label">mAP (平均精度)</div>
                  <div class="metric-value">{{ parsedResults.summary.mAP.toFixed(4) }}</div>
                </div>
                <div class="metric-card" v-if="parsedResults.summary.mATE !== undefined">
                  <div class="metric-label">mATE (平均平移误差)</div>
                  <div class="metric-value">{{ parsedResults.summary.mATE.toFixed(4) }}</div>
                </div>
                <div class="metric-card" v-if="parsedResults.summary.mASE !== undefined">
                  <div class="metric-label">mASE (平均尺度误差)</div>
                  <div class="metric-value">{{ parsedResults.summary.mASE.toFixed(4) }}</div>
                </div>
                <div class="metric-card" v-if="parsedResults.summary.mAOE !== undefined">
                  <div class="metric-label">mAOE (平均方向误差)</div>
                  <div class="metric-value">{{ parsedResults.summary.mAOE.toFixed(4) }}</div>
                </div>
                <div class="metric-card" v-if="parsedResults.summary.mAVE !== undefined">
                  <div class="metric-label">mAVE (平均速度误差)</div>
                  <div class="metric-value">{{ parsedResults.summary.mAVE.toFixed(4) }}</div>
                </div>
              </div>
            </div>
            
            <!-- 每类别结果表格 -->
            <div class="per-class-section" v-if="parsedResults.perClass.length > 0">
              <h4>各类别检测结果</h4>
              <div class="table-wrapper">
                <table class="results-table">
                  <thead>
                    <tr>
                      <th>类别</th>
                      <th>AP (精度)</th>
                      <th>ATE (平移误差)</th>
                      <th>ASE (尺度误差)</th>
                      <th>AOE (方向误差)</th>
                      <th>AVE (速度误差)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in parsedResults.perClass" :key="item.class">
                      <td class="class-name">{{ item.class }}</td>
                      <td>{{ item.AP.toFixed(3) }}</td>
                      <td>{{ item.ATE.toFixed(3) }}</td>
                      <td>{{ item.ASE.toFixed(3) }}</td>
                      <td>{{ item.AOE.toFixed(3) }}</td>
                      <td>{{ item.AVE.toFixed(3) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <!-- 规划指标 -->
            <div class="planning-section" v-if="parsedResults.planningMetrics.length > 0">
              <h4>规划评估指标</h4>
              <div class="table-wrapper">
                <table class="results-table">
                  <thead>
                    <tr>
                      <th>指标</th>
                      <th v-for="val in parsedResults.planningMetrics[0].values" :key="val.time">
                        {{ val.time }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="metric in parsedResults.planningMetrics" :key="metric.name">
                      <td class="metric-name">{{ metric.name }}</td>
                      <td v-for="val in metric.values" :key="val.time">
                        {{ val.value.toFixed(4) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <!-- 详细检测指标 -->
            <div class="detailed-section" v-if="parsedResults.detailedMetrics.length > 0">
              <h4>各类别详细检测指标</h4>
              
              <div v-for="classMetric in parsedResults.detailedMetrics" :key="classMetric.class" class="class-detail">
                <h5>{{ classMetric.class }}</h5>
                
                <div class="metrics-row">
                  <div class="metric-group">
                    <div class="group-title">不同距离的AP (精度)</div>
                    <div class="metric-items">
                      <div v-for="(value, dist) in classMetric.AP_dist" :key="dist" class="metric-item">
                        <span class="item-label">{{ dist }}:</span>
                        <span class="item-value">{{ value.toFixed(4) }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="metric-group">
                    <div class="group-title">误差指标</div>
                    <div class="metric-items">
                      <div v-for="(value, errType) in classMetric.errors" :key="errType" class="metric-item">
                        <span class="item-label">{{ getErrorTypeName(errType) }}:</span>
                        <span class="item-value">{{ value.toFixed(4) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="no-result">
            <p>暂无测试结果</p>
          </div>
        </div>
        
        <div class="dialog-footer">
          <button @click="exportPDF" class="export-btn" :disabled="loadingResult || !parsedResults">
            {{ exportingPDF ? '导出中...' : '导出PDF报告' }}
          </button>
          <button @click="closeResultDialog" class="confirm-btn">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTrainingRecords } from '../api/trainingRecords'
import api from '../api/auth'
import jsPDF from 'jspdf'

const trainingRecords = ref([])
const loading = ref(true)
const filterStatus = ref('')
const filterTime = ref('')
const searchId = ref('')
const sortBy = ref('')

const showTestDialog = ref(false)
const showResultDialog = ref(false)
const currentTestingId = ref(null)
const currentResultId = ref(null)
const loadingResult = ref(false)
const resultLogContent = ref('')
const testing = ref(false)
const parsedResults = ref(null)
const exportingPDF = ref(false)

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
  
  // 过滤掉"训练中"状态的记录
  records = records.filter(r => r.status !== 'Training')
  
  // 按ID搜索
  if (searchId.value) {
    const searchTerm = searchId.value.trim()
    records = records.filter(r => 
      String(r.training_id).includes(searchTerm)
    )
  }
  
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
  
  // 排序
  if (sortBy.value) {
    records.sort((a, b) => {
      switch (sortBy.value) {
        case 'render_cost':
          return (a.render_cost || 0) - (b.render_cost || 0) // 成本：低到高
        case 'train_cost':
          return (a.train_cost || 0) - (b.train_cost || 0) // 成本：低到高
        case 'test_score':
          return (b.test_score || 0) - (a.test_score || 0) // 分数：高到低
        case 'total_score':
          return (b.total_score || 0) - (a.total_score || 0) // 分数：高到低
        default:
          return 0
      }
    })
  }
  
  return records
})

const startTest = (trainingId) => {
  currentTestingId.value = trainingId
  showTestDialog.value = true
}

const closeTestDialog = () => {
  showTestDialog.value = false
  currentTestingId.value = null
}

const confirmTest = async () => {
  if (!currentTestingId.value) return
  
  testing.value = true
  const trainingId = currentTestingId.value // 保存ID，避免在setTimeout中丢失
  
  try {
    // 更新状态为 Testing
    await api.put(`/training/records/${trainingId}/status`, { status: 'Testing' })
    
    // 更新本地记录
    const record = trainingRecords.value.find(r => r.training_id === trainingId)
    if (record) {
      record.status = 'Testing'
    }
    
    closeTestDialog()
    
   
    const delay = Math.floor(Math.random() * 5000) + 10000 
    setTimeout(async () => {
      try {
        const response = await api.put(`/training/records/${trainingId}/status`, { 
          status: 'Tested'
        })
        
        // 更新本地记录，包括分数
        if (record && response.data && response.data.data) {
          record.status = 'Tested'
          record.test_score = response.data.data.test_score
          record.total_score = response.data.data.total_score
        }
      } catch (error) {
        console.error('更新测试状态失败:', error)
      }
    }, delay)
    
  } catch (error) {
    console.error('生成测试失败:', error)
    const errorMsg = error.response?.data?.error || '生成测试失败'
    alert(errorMsg)
  } finally {
    testing.value = false
  }
}

const parseLogResults = (logContent) => {
  const results = {
    summary: {},
    perClass: [],
    planningMetrics: [],
    detailedMetrics: []
  }
  
  try {
    // 提取总体指标 (NDS, mAP, mATE, mASE, mAOE, mAVE)
    const ndsMatch = logContent.match(/NDS:\s*([\d.]+)/)
    if (ndsMatch) results.summary.NDS = parseFloat(ndsMatch[1])
    
    const mapMatch = logContent.match(/mAP:\s*([\d.]+)/)
    if (mapMatch) results.summary.mAP = parseFloat(mapMatch[1])
    
    const mateMatch = logContent.match(/mATE:\s*([\d.]+)/)
    if (mateMatch) results.summary.mATE = parseFloat(mateMatch[1])
    
    const maseMatch = logContent.match(/mASE:\s*([\d.]+)/)
    if (maseMatch) results.summary.mASE = parseFloat(maseMatch[1])
    
    const maoeMatch = logContent.match(/mAOE:\s*([\d.]+)/)
    if (maoeMatch) results.summary.mAOE = parseFloat(maoeMatch[1])
    
    const maveMatch = logContent.match(/mAVE:\s*([\d.]+)/)
    if (maveMatch) results.summary.mAVE = parseFloat(maveMatch[1])
    
    // 提取每个类别的结果
    const perClassSection = logContent.match(/Per-class results:([\s\S]*?)(?=\+---|$)/)
    if (perClassSection) {
      const lines = perClassSection[1].trim().split('\n')
      for (let i = 1; i < lines.length; i++) { // 跳过表头
        const parts = lines[i].split(/\s+/)
        if (parts.length >= 5 && parts[0] !== 'Object') {
          results.perClass.push({
            class: parts[0],
            AP: parseFloat(parts[1]),
            ATE: parseFloat(parts[2]),
            ASE: parseFloat(parts[3]),
            AOE: parseFloat(parts[4]),
            AVE: parseFloat(parts[5])
          })
        }
      }
    }
    
    // 提取规划指标表格
    const planningMatch = logContent.match(/\+[-+]+\+\s*\n\s*\|\s*metrics\s*\|([\s\S]*?)\+[-+]+\+/)
    if (planningMatch) {
      const fullTable = planningMatch[0]
      const lines = fullTable.split('\n').filter(line => line.trim().length > 0)
      
      // 找到表头行（包含 metrics）
      let headerLine = null
      let dataStartIndex = -1
      
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes('metrics')) {
          headerLine = lines[i]
          dataStartIndex = i + 2 // 跳过表头和分隔线
          break
        }
      }
      
      if (headerLine && dataStartIndex > 0) {
        // 解析表头
        const headerParts = headerLine.split('|').map(s => s.trim()).filter(s => s && s !== '')
        const timeSteps = headerParts.slice(1) // 跳过 "metrics"
        
        // 解析数据行
        for (let i = dataStartIndex; i < lines.length; i++) {
          const line = lines[i]
          if (line.includes('|') && !line.includes('+') && !line.includes('-')) {
            const parts = line.split('|').map(s => s.trim()).filter(s => s && s !== '')
            if (parts.length > 1) {
              const metric = {
                name: parts[0],
                values: []
              }
              for (let j = 1; j < parts.length && j <= timeSteps.length; j++) {
                metric.values.push({
                  time: timeSteps[j - 1],
                  value: parseFloat(parts[j])
                })
              }
              results.planningMetrics.push(metric)
            }
          }
        }
      }
    }
    
    // 提取详细的 bbox_NuScenes 指标
    const detailedMatch = logContent.match(/Epoch\(val\).*?bbox_NuScenes\/([\s\S]*?)(?=\n\n|$)/)
    if (detailedMatch) {
      const metricsText = detailedMatch[0]
      
      // 提取所有类别
      const classes = ['car', 'van', 'truck', 'bicycle', 'traffic_sign', 'traffic_cone', 'traffic_light', 'pedestrian']
      
      classes.forEach(className => {
        const classMetrics = {
          class: className,
          AP_dist: {},
          errors: {}
        }
        
        // 提取 AP_dist 指标
        const apDistances = ['0.5', '1.0', '2.0', '4.0']
        apDistances.forEach(dist => {
          const pattern = new RegExp(`${className}_AP_dist_${dist.replace('.', '\\.')}:\\s*([\\d.]+)`)
          const match = metricsText.match(pattern)
          if (match) {
            classMetrics.AP_dist[`${dist}m`] = parseFloat(match[1])
          }
        })
        
        // 提取误差指标
        const errorTypes = ['trans_err', 'scale_err', 'orient_err', 'vel_err']
        errorTypes.forEach(errType => {
          const pattern = new RegExp(`${className}_${errType}:\\s*([\\d.]+)`)
          const match = metricsText.match(pattern)
          if (match) {
            classMetrics.errors[errType] = parseFloat(match[1])
          }
        })
        
        results.detailedMetrics.push(classMetrics)
      })
    }
  } catch (error) {
    console.error('解析日志失败:', error)
  }
  
  return results
}

const viewResult = async (trainingId) => {
  currentResultId.value = trainingId
  showResultDialog.value = true
  loadingResult.value = true
  resultLogContent.value = ''
  parsedResults.value = null
  
  try {
    // 获取训练日志
    const response = await api.get(`/training/logs/${trainingId}`)
    const fullLog = response.data.data
    
    // 提取 "Per-class results:" 之后的内容
    const perClassIndex = fullLog.indexOf('Per-class results:')
    if (perClassIndex !== -1) {
      const logSection = fullLog.substring(perClassIndex)
      resultLogContent.value = logSection
      parsedResults.value = parseLogResults(logSection)
    } else {
      resultLogContent.value = '未找到测试结果数据'
    }
  } catch (error) {
    console.error('加载测试结果失败:', error)
    resultLogContent.value = '加载测试结果失败'
  } finally {
    loadingResult.value = false
  }
}

const closeResultDialog = () => {
  showResultDialog.value = false
  currentResultId.value = null
  resultLogContent.value = ''
}

const getErrorTypeName = (errType) => {
  const errorTypeMap = {
    'trans_err': 'trans_err (平移误差)',
    'scale_err': 'scale_err (尺度误差)',
    'orient_err': 'orient_err (方向误差)',
    'vel_err': 'vel_err (速度误差)'
  }
  return errorTypeMap[errType] || errType
}

const exportPDF = async () => {
  if (!parsedResults.value) return
  
  exportingPDF.value = true
  
  try {
    const doc = new jsPDF()
    let yPos = 20
    
    // 标题
    doc.setFontSize(16)
    doc.text(`Training ${currentResultId.value} - Evaluation Report`, 20, yPos)
    yPos += 15
    
    // 总体评估指标
    doc.setFontSize(12)
    doc.text('Overall Evaluation Metrics', 20, yPos)
    yPos += 8
    
    doc.setFontSize(10)
    const summary = parsedResults.value.summary
    if (summary.NDS !== undefined) {
      doc.text(`NDS (Driving Detection Score): ${summary.NDS.toFixed(4)}`, 25, yPos)
      yPos += 6
    }
    if (summary.mAP !== undefined) {
      doc.text(`mAP (Mean Average Precision): ${summary.mAP.toFixed(4)}`, 25, yPos)
      yPos += 6
    }
    if (summary.mATE !== undefined) {
      doc.text(`mATE (Mean Translation Error): ${summary.mATE.toFixed(4)}`, 25, yPos)
      yPos += 6
    }
    if (summary.mASE !== undefined) {
      doc.text(`mASE (Mean Scale Error): ${summary.mASE.toFixed(4)}`, 25, yPos)
      yPos += 6
    }
    if (summary.mAOE !== undefined) {
      doc.text(`mAOE (Mean Orientation Error): ${summary.mAOE.toFixed(4)}`, 25, yPos)
      yPos += 6
    }
    if (summary.mAVE !== undefined) {
      doc.text(`mAVE (Mean Velocity Error): ${summary.mAVE.toFixed(4)}`, 25, yPos)
      yPos += 10
    }
    
    // 各类别检测结果
    if (parsedResults.value.perClass.length > 0) {
      if (yPos > 250) {
        doc.addPage()
        yPos = 20
      }
      
      doc.setFontSize(12)
      doc.text('Per-Class Detection Results', 20, yPos)
      yPos += 8
      
      doc.setFontSize(9)
      parsedResults.value.perClass.forEach(item => {
        if (yPos > 270) {
          doc.addPage()
          yPos = 20
        }
        doc.text(`${item.class}: AP=${item.AP.toFixed(3)}, ATE=${item.ATE.toFixed(3)}, ASE=${item.ASE.toFixed(3)}, AOE=${item.AOE.toFixed(3)}, AVE=${item.AVE.toFixed(3)}`, 25, yPos)
        yPos += 6
      })
      yPos += 5
    }
    
    // 规划评估指标
    if (parsedResults.value.planningMetrics.length > 0) {
      if (yPos > 250) {
        doc.addPage()
        yPos = 20
      }
      
      doc.setFontSize(12)
      doc.text('Planning Evaluation Metrics', 20, yPos)
      yPos += 8
      
      doc.setFontSize(9)
      parsedResults.value.planningMetrics.forEach(metric => {
        if (yPos > 270) {
          doc.addPage()
          yPos = 20
        }
        const values = metric.values.map(v => `${v.time}:${v.value.toFixed(4)}`).join(', ')
        doc.text(`${metric.name}: ${values}`, 25, yPos)
        yPos += 6
      })
      yPos += 5
    }
    
    // 详细检测指标
    if (parsedResults.value.detailedMetrics.length > 0) {
      if (yPos > 230) {
        doc.addPage()
        yPos = 20
      }
      
      doc.setFontSize(12)
      doc.text('Detailed Detection Metrics', 20, yPos)
      yPos += 8
      
      doc.setFontSize(8)
      parsedResults.value.detailedMetrics.forEach(classMetric => {
        if (yPos > 260) {
          doc.addPage()
          yPos = 20
        }
        
        doc.setFontSize(9)
        doc.text(`${classMetric.class}:`, 25, yPos)
        yPos += 5
        
        doc.setFontSize(8)
        // AP距离
        const apDist = Object.entries(classMetric.AP_dist).map(([k, v]) => `${k}:${v.toFixed(4)}`).join(', ')
        doc.text(`  AP_dist: ${apDist}`, 30, yPos)
        yPos += 5
        
        // 误差指标
        const errors = Object.entries(classMetric.errors).map(([k, v]) => `${k}:${v.toFixed(4)}`).join(', ')
        doc.text(`  Errors: ${errors}`, 30, yPos)
        yPos += 7
      })
    }
    
    // 保存PDF
    doc.save(`training_${currentResultId.value}_report.pdf`)
    
  } catch (error) {
    console.error('导出PDF失败:', error)
    alert('导出PDF失败')
  } finally {
    exportingPDF.value = false
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
  border-color: #42b983;
}

.search-input:focus {
  outline: none;
  border-color: #42b983;
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

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s;
}

.test-btn {
  background: #42b983;
  color: white;
}

.test-btn:hover {
  background: #359268;
}

.result-btn {
  background: #667eea;
  color: white;
}

.result-btn:hover {
  background: #5568d3;
}

.action-btn:focus {
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
  max-width: 500px;
  display: flex;
  flex-direction: column;
}

.result-dialog {
  max-width: 800px;
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

.dialog-body {
  padding: 2rem 1.5rem;
}

.dialog-body p {
  margin: 0 0 1.5rem 0;
  color: #555;
  font-size: 1rem;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.result-label {
  font-weight: 600;
  color: #555;
}

.result-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #42b983;
}

.results-container {
  max-height: 600px;
  overflow-y: auto;
  padding: 0.5rem;
}

.summary-section,
.per-class-section,
.planning-section {
  margin-bottom: 2rem;
}

.summary-section h4,
.per-class-section h4,
.planning-section h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #42b983;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 0.75rem;
}

.metric-card {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.75rem;
  border-radius: 6px;
  text-align: center;
}

.metric-label {
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0.4rem;
  font-weight: 500;
}

.metric-value {
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
}

.table-wrapper {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.results-table thead {
  background: #42b983;
  color: white;
}

.results-table th {
  padding: 0.75rem;
  text-align: center;
  font-weight: 600;
  font-size: 0.85rem;
}

.results-table tbody tr {
  border-bottom: 1px solid #e9ecef;
  transition: background 0.2s;
}

.results-table tbody tr:hover {
  background: #f8f9fa;
}

.results-table tbody tr:last-child {
  border-bottom: none;
}

.results-table td {
  padding: 0.75rem;
  text-align: center;
  color: #555;
}

.results-table .class-name,
.results-table .metric-name {
  font-weight: 600;
  color: #333;
  text-align: left;
  padding-left: 1rem;
}

.no-result {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.detailed-section {
  margin-bottom: 2rem;
}

.detailed-section h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #42b983;
}

.class-detail {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.class-detail h5 {
  margin: 0 0 0.75rem 0;
  color: #333;
  font-size: 0.95rem;
  font-weight: 600;
  text-transform: capitalize;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.metric-group {
  background: white;
  padding: 0.75rem;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.group-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.metric-items {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.item-label {
  color: #666;
  font-weight: 500;
}

.item-value {
  color: #333;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #dee2e6;
}

.cancel-btn,
.confirm-btn,
.export-btn {
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

.export-btn {
  background: #667eea;
  color: white;
}

.export-btn:hover:not(:disabled) {
  background: #5568d3;
}

.export-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

</style>
