<template>
  <div v-if="show" class="dialog-overlay" @click="$emit('close')">
    <div class="dialog-content training-info-dialog" @click.stop>
      <div class="dialog-header">
        <h3>训练信息 - 训练ID: {{ trainingId }}</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
      <div class="dialog-body">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="error" class="error-message">{{ error }}</div>
        <div v-else-if="trainingInfo" class="training-info-wrapper">
          <!-- 导航栏 -->
          <div class="stage-nav">
            <button @click="showLossChart = !showLossChart" class="chart-btn">
              {{ showLossChart ? '返回详情' : '损失曲线' }}
            </button>
            
            <div v-if="!showLossChart" class="epoch-nav-container">
              <div v-for="epoch in epochGroups" :key="epoch.number" class="epoch-row">
                <div class="epoch-label">Epoch {{ epoch.number }}</div>
                <div class="step-buttons">
                  <button 
                    v-for="stage in epoch.stages" 
                    :key="stage.index"
                    @click="currentStageIndex = stage.index"
                    :class="['nav-btn', { active: currentStageIndex === stage.index }]"
                  >
                    Step {{ stage.step }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 损失曲线图表 -->
          <div v-if="showLossChart" class="chart-view">
            <!-- 图表分类导航 -->
            <div class="chart-nav">
              <button 
                v-for="cat in chartCategories"
                :key="cat.value"
                @click="currentChartCategory = cat.value"
                :class="['chart-nav-btn', { active: currentChartCategory === cat.value }]"
              >
                {{ cat.label }}
              </button>
            </div>
            
            <!-- 图表容器 -->
            <div class="chart-container">
              <div v-if="currentChartCategory === 'track_cls_f0'" class="chart-section">
                <h5>Track Classification Loss - Frame 0</h5>
                <canvas ref="trackClsF0Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'track_cls_f1'" class="chart-section">
                <h5>Track Classification Loss - Frame 1</h5>
                <canvas ref="trackClsF1Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'track_cls_f2'" class="chart-section">
                <h5>Track Classification Loss - Frame 2</h5>
                <canvas ref="trackClsF2Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'track_bbox_f0'" class="chart-section">
                <h5>Track BBox Loss - Frame 0</h5>
                <canvas ref="trackBboxF0Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'track_bbox_f1'" class="chart-section">
                <h5>Track BBox Loss - Frame 1</h5>
                <canvas ref="trackBboxF1Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'track_bbox_f2'" class="chart-section">
                <h5>Track BBox Loss - Frame 2</h5>
                <canvas ref="trackBboxF2Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'track_traj_f0'" class="chart-section">
                <h5>Track Past Trajectories Loss - Frame 0</h5>
                <canvas ref="trackTrajF0Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'track_traj_f1'" class="chart-section">
                <h5>Track Past Trajectories Loss - Frame 1</h5>
                <canvas ref="trackTrajF1Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'track_traj_f2'" class="chart-section">
                <h5>Track Past Trajectories Loss - Frame 2</h5>
                <canvas ref="trackTrajF2Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'map_main'" class="chart-section">
                <h5>Map Main Losses</h5>
                <canvas ref="mapMainChart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'map_d0'" class="chart-section">
                <h5>Map D0 Layer Losses</h5>
                <canvas ref="mapD0Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'map_d1'" class="chart-section">
                <h5>Map D1 Layer Losses</h5>
                <canvas ref="mapD1Chart"></canvas>
              </div>
              <div v-if="currentChartCategory === 'map_d2'" class="chart-section">
                <h5>Map D2 Layer Losses</h5>
                <canvas ref="mapD2Chart"></canvas>
              </div>
            </div>
          </div>
          
          <!-- 当前阶段信息 -->
          <div v-if="!showLossChart && currentStage" class="training-info-container">
            <div class="stage-header">
              <h4>Epoch [{{ currentStage.epoch }}][{{ currentStage.step }}/{{ currentStage.totalSteps }}]</h4>
            </div>
            
            <!-- Track 损失 -->
            <div class="info-section">
              <h5>Track 损失指标</h5>
              
              <div v-for="frameNum in [0, 1, 2]" :key="frameNum" class="frame-group">
                <div class="frame-title">帧 {{ frameNum }}</div>
                <div class="loss-types">
                  <div class="loss-type-group">
                    <div class="type-label">分类损失 (Classification Loss)</div>
                    <div class="layer-grid">
                      <div v-for="item in currentStage.trackLosses[`frame_${frameNum}`].cls" :key="item.layer" class="layer-item">
                        <span class="layer-num">L{{ item.layer }}</span>
                        <span class="layer-val">{{ item.value }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="loss-type-group">
                    <div class="type-label">边界框损失 (BBox Loss)</div>
                    <div class="layer-grid">
                      <div v-for="item in currentStage.trackLosses[`frame_${frameNum}`].bbox" :key="item.layer" class="layer-item">
                        <span class="layer-num">L{{ item.layer }}</span>
                        <span class="layer-val">{{ item.value }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="loss-type-group">
                    <div class="type-label">历史轨迹损失 (Past Trajectories Loss)</div>
                    <div class="layer-grid">
                      <div v-for="item in currentStage.trackLosses[`frame_${frameNum}`].past_trajs" :key="item.layer" class="layer-item">
                        <span class="layer-num">L{{ item.layer }}</span>
                        <span class="layer-val">{{ item.value }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Map 损失 -->
            <div class="info-section">
              <h5>Map 损失指标</h5>
              
              <div class="map-group">
                <div class="map-title">主要损失 (Main Losses)</div>
                <div class="metrics-grid">
                  <div v-for="(value, key) in currentStage.mapLosses.main" :key="key" class="metric-item">
                    <div class="metric-label">{{ key }}</div>
                    <div class="metric-value">{{ value }}</div>
                  </div>
                </div>
              </div>
              
              <div v-for="layer in ['d0', 'd1', 'd2']" :key="layer">
                <div v-if="Object.keys(currentStage.mapLosses[layer]).length > 0" class="map-group">
                  <div class="map-title">{{ layer.toUpperCase() }} 层损失 ({{ layer.toUpperCase() }} Losses)</div>
                  <div class="metrics-grid">
                    <div v-for="(value, key) in currentStage.mapLosses[layer]" :key="key" class="metric-item">
                      <div class="metric-label">{{ key }}</div>
                      <div class="metric-value">{{ value }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 其他损失 -->
            <div v-if="Object.keys(currentStage.otherLosses).length > 0" class="info-section">
              <h5>其他损失指标</h5>
              
              <div v-if="currentStage.otherLosses.motion && Object.keys(currentStage.otherLosses.motion).length > 0" class="other-group">
                <div class="other-title">运动损失 (Motion Losses)</div>
                <div class="metrics-grid">
                  <div v-for="(value, key) in currentStage.otherLosses.motion" :key="key" class="metric-item">
                    <div class="metric-label">{{ key }}</div>
                    <div class="metric-value">{{ value }}</div>
                  </div>
                </div>
              </div>
              
              <div v-if="currentStage.otherLosses.occ && Object.keys(currentStage.otherLosses.occ).length > 0" class="other-group">
                <div class="other-title">占用损失 (Occupancy Losses)</div>
                <div class="metrics-grid">
                  <div v-for="(value, key) in currentStage.otherLosses.occ" :key="key" class="metric-item">
                    <div class="metric-label">{{ key }}</div>
                    <div class="metric-value">{{ value }}</div>
                  </div>
                </div>
              </div>
              
              <div v-if="currentStage.otherLosses.planning && Object.keys(currentStage.otherLosses.planning).length > 0" class="other-group">
                <div class="other-title">规划损失 (Planning Losses)</div>
                <div class="metrics-grid">
                  <div v-for="(value, key) in currentStage.otherLosses.planning" :key="key" class="metric-item">
                    <div class="metric-label">{{ key }}</div>
                    <div class="metric-value">{{ value }}</div>
                  </div>
                </div>
              </div>
              
              <div v-if="currentStage.otherLosses.uncategorized && Object.keys(currentStage.otherLosses.uncategorized).length > 0" class="other-group">
                <div class="other-title">未分类损失 (Uncategorized Losses)</div>
                <div class="metrics-grid">
                  <div v-for="(value, key) in currentStage.otherLosses.uncategorized" :key="key" class="metric-item">
                    <div class="metric-label">{{ key }}</div>
                    <div class="metric-value">{{ value }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import axios from 'axios'
import {
  parseTrainingLog,
  getEpochGroups,
  drawTrackClsF0Chart,
  drawTrackClsF1Chart,
  drawTrackClsF2Chart,
  drawTrackBboxF0Chart,
  drawTrackBboxF1Chart,
  drawTrackBboxF2Chart,
  drawTrackTrajF0Chart,
  drawTrackTrajF1Chart,
  drawTrackTrajF2Chart,
  drawMapMainChart,
  drawMapD0Chart,
  drawMapD1Chart,
  drawMapD2Chart
} from '../utils/trainingCharts'

const props = defineProps({
  show: Boolean,
  trainingId: Number
})

const emit = defineEmits(['close'])

const loading = ref(false)
const error = ref('')
const trainingInfo = ref(null)
const currentStageIndex = ref(0)
const showLossChart = ref(false)
const currentChartCategory = ref('track_cls_f0')

// 图表分类
const chartCategories = [
  { value: 'track_cls_f0', label: 'Track 分类 Frame 0' },
  { value: 'track_cls_f1', label: 'Track 分类 Frame 1' },
  { value: 'track_cls_f2', label: 'Track 分类 Frame 2' },
  { value: 'track_bbox_f0', label: 'Track 边界框 Frame 0' },
  { value: 'track_bbox_f1', label: 'Track 边界框 Frame 1' },
  { value: 'track_bbox_f2', label: 'Track 边界框 Frame 2' },
  { value: 'track_traj_f0', label: 'Track 轨迹 Frame 0' },
  { value: 'track_traj_f1', label: 'Track 轨迹 Frame 1' },
  { value: 'track_traj_f2', label: 'Track 轨迹 Frame 2' },
  { value: 'map_main', label: 'Map 主要损失' },
  { value: 'map_d0', label: 'Map D0 层' },
  { value: 'map_d1', label: 'Map D1 层' },
  { value: 'map_d2', label: 'Map D2 层' }
]

// 图表引用
const trackClsF0Chart = ref(null)
const trackClsF1Chart = ref(null)
const trackClsF2Chart = ref(null)
const trackBboxF0Chart = ref(null)
const trackBboxF1Chart = ref(null)
const trackBboxF2Chart = ref(null)
const trackTrajF0Chart = ref(null)
const trackTrajF1Chart = ref(null)
const trackTrajF2Chart = ref(null)
const mapMainChart = ref(null)
const mapD0Chart = ref(null)
const mapD1Chart = ref(null)
const mapD2Chart = ref(null)

let chartInstances = {}

const epochGroups = computed(() => {
  return trainingInfo.value ? getEpochGroups(trainingInfo.value.stages) : []
})

const currentStage = computed(() => {
  return trainingInfo.value?.stages[currentStageIndex.value]
})

// 加载训练信息
const loadTrainingInfo = async () => {
  if (!props.trainingId) return
  
  loading.value = true
  error.value = ''
  trainingInfo.value = null
  currentStageIndex.value = 0
  showLossChart.value = false
  
  try {
    const response = await axios.get(`/api/training/logs/${props.trainingId}`)
    const logContent = response.data.data
    trainingInfo.value = parseTrainingLog(logContent)
    
    if (!trainingInfo.value) {
      error.value = '未找到训练信息'
    }
  } catch (err) {
    console.error('加载训练信息失败:', err)
    error.value = err.response?.data?.error || '加载训练信息失败'
  } finally {
    loading.value = false
  }
}

// 绘制当前图表
const drawCurrentChart = () => {
  console.log('drawCurrentChart called, category:', currentChartCategory.value)
  console.log('trainingInfo:', trainingInfo.value)
  
  const chartMap = {
    track_cls_f0: { ref: trackClsF0Chart, fn: drawTrackClsF0Chart },
    track_cls_f1: { ref: trackClsF1Chart, fn: drawTrackClsF1Chart },
    track_cls_f2: { ref: trackClsF2Chart, fn: drawTrackClsF2Chart },
    track_bbox_f0: { ref: trackBboxF0Chart, fn: drawTrackBboxF0Chart },
    track_bbox_f1: { ref: trackBboxF1Chart, fn: drawTrackBboxF1Chart },
    track_bbox_f2: { ref: trackBboxF2Chart, fn: drawTrackBboxF2Chart },
    track_traj_f0: { ref: trackTrajF0Chart, fn: drawTrackTrajF0Chart },
    track_traj_f1: { ref: trackTrajF1Chart, fn: drawTrackTrajF1Chart },
    track_traj_f2: { ref: trackTrajF2Chart, fn: drawTrackTrajF2Chart },
    map_main: { ref: mapMainChart, fn: drawMapMainChart },
    map_d0: { ref: mapD0Chart, fn: drawMapD0Chart },
    map_d1: { ref: mapD1Chart, fn: drawMapD1Chart },
    map_d2: { ref: mapD2Chart, fn: drawMapD2Chart }
  }
  
  const chart = chartMap[currentChartCategory.value]
  console.log('chart ref:', chart?.ref.value)
  console.log('chart ref exists:', !!chart?.ref.value)
  
  if (chart && chart.ref.value && trainingInfo.value) {
    console.log('Calling chart function...')
    const instance = chart.fn(chart.ref.value, trainingInfo.value, chartInstances[currentChartCategory.value])
    console.log('Chart instance created:', instance)
    if (instance) {
      chartInstances[currentChartCategory.value] = instance
    }
  } else {
    console.log('Chart drawing skipped - missing requirements')
  }
}

// 监听显示状态
watch(() => props.show, (newVal) => {
  if (newVal) {
    loadTrainingInfo()
  } else {
    // 清理图表实例
    Object.values(chartInstances).forEach(instance => {
      if (instance) instance.destroy()
    })
    chartInstances = {}
  }
})

// 监听图表切换
watch(showLossChart, async (newVal) => {
  if (newVal && trainingInfo.value) {
    await nextTick()
    await nextTick()
    setTimeout(() => {
      drawCurrentChart()
    }, 100)
  }
})

watch(currentChartCategory, async () => {
  if (showLossChart.value && trainingInfo.value) {
    await nextTick()
    setTimeout(() => {
      drawCurrentChart()
    }, 50)
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
  max-width: 1000px;
  max-height: 95vh;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
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
  padding: 1.5rem;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  min-height: 0;
}

.loading, .error-message {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error-message {
  color: #c62828;
}

.stage-nav {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border-bottom: 2px solid #eee;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.chart-btn {
  padding: 0.6rem 1.5rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.95rem;
  margin-bottom: 1rem;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-block;
}

.chart-btn:hover {
  background: #359268;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(66, 185, 131, 0.3);
}

.epoch-nav-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 250px;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0.5rem;
  background: #fafafa;
  border-radius: 4px;
}

.epoch-row {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.75rem;
  background: white;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
  flex-wrap: nowrap;
}

.epoch-label {
  font-weight: bold;
  color: #555;
  min-width: 90px;
  padding-top: 0.5rem;
  flex-shrink: 0;
  font-size: 0.9rem;
}

.step-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.nav-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s;
  white-space: nowrap;
  flex-shrink: 0;
}

.nav-btn:hover {
  border-color: #42b983;
  color: #42b983;
  transform: translateY(-1px);
}

.nav-btn.active {
  background: #42b983;
  color: white;
  border-color: #42b983;
  font-weight: 600;
}

.chart-nav {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.chart-nav-btn {
  padding: 0.6rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s;
  text-align: center;
  word-wrap: break-word;
  word-break: keep-all;
  line-height: 1.4;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-nav-btn:hover {
  border-color: #42b983;
  color: #42b983;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-nav-btn.active {
  background: #42b983;
  color: white;
  border-color: #42b983;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(66, 185, 131, 0.3);
}

.chart-container {
  background: #fafafa;
  padding: 1.5rem;
  border-radius: 6px;
  min-height: 450px;
}

.chart-section {
  min-height: 450px;
  display: flex;
  flex-direction: column;
}

.chart-section h5 {
  margin: 0 0 1rem 0;
  color: #555;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.chart-section canvas {
  flex: 1;
  min-height: 400px;
  max-height: 500px;
}

.training-info-container {
  background: #fafafa;
  padding: 1.5rem;
  border-radius: 6px;
  overflow-x: hidden;
}

.stage-header h4 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.2rem;
}

.info-section {
  margin-bottom: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: 6px;
  overflow: hidden;
}

.info-section h5 {
  margin: 0 0 1.5rem 0;
  color: #555;
  font-size: 1.1rem;
  border-bottom: 2px solid #eee;
  padding-bottom: 0.5rem;
}

.frame-group, .map-group, .other-group {
  margin-bottom: 1.5rem;
  padding: 1.2rem;
  background: #f9f9f9;
  border-radius: 4px;
  border-left: 3px solid #42b983;
}

.frame-title, .map-title, .other-title {
  font-weight: bold;
  color: #333;
  margin-bottom: 1rem;
  font-size: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.loss-types {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.loss-type-group {
  background: white;
  padding: 1rem;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.type-label {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.layer-grid, .metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.layer-item, .metric-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0.6rem 0.8rem;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 0.85rem;
  border: 1px solid #e8e8e8;
  transition: all 0.2s;
  min-height: 48px;
  gap: 0.3rem;
}

.layer-item:hover, .metric-item:hover {
  background: #ebebeb;
  border-color: #42b983;
}

.layer-num, .metric-label {
  color: #666;
  font-weight: 600;
  word-wrap: break-word;
  word-break: break-word;
  width: 100%;
  font-size: 0.8rem;
}

.layer-val, .metric-value {
  color: #333;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  word-wrap: break-word;
  word-break: break-all;
  width: 100%;
  font-size: 0.9rem;
}
</style>
