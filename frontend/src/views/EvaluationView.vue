<template>
  <div class="evaluation-view">
    <h2>测试评估</h2>
    
    <div class="evaluation-container">
      <div class="section">
        <h3>选择训练记录</h3>
        <div v-if="trainingRecords.length === 0" class="empty-message">
          <p>暂无已完成的训练记录</p>
        </div>
        <div v-else class="records-grid">
          <div 
            v-for="record in completedRecords" 
            :key="record.id" 
            class="record-item"
            :class="{ 'selected': selectedRecord?.id === record.id }"
            @click="selectRecord(record)">
            <div class="record-id">{{ record.id }}</div>
            <div class="record-time">{{ record.createdAt }}</div>
            <div class="record-status">已完成</div>
          </div>
        </div>
      </div>

      <div v-if="selectedRecord" class="section">
        <h3>测试配置</h3>
        <div class="config-form">
          <div class="form-group">
            <label>测试数据集：</label>
            <select v-model="testConfig.dataset">
              <option value="test_set_1">测试集1</option>
              <option value="test_set_2">测试集2</option>
              <option value="validation_set">验证集</option>
            </select>
          </div>
          <div class="form-group">
            <label>评估指标：</label>
            <div class="checkbox-group">
              <label><input type="checkbox" v-model="testConfig.metrics.accuracy"> 准确率</label>
              <label><input type="checkbox" v-model="testConfig.metrics.precision"> 精确率</label>
              <label><input type="checkbox" v-model="testConfig.metrics.recall"> 召回率</label>
              <label><input type="checkbox" v-model="testConfig.metrics.f1"> F1分数</label>
            </div>
          </div>
          <div class="form-group">
            <label>批次大小：</label>
            <input type="number" v-model.number="testConfig.batchSize" min="1" max="128">
          </div>
        </div>
        
        <div class="action-buttons">
          <button @click="startEvaluation" :disabled="evaluating" class="start-eval-btn">
            {{ evaluating ? '评估中...' : '开始评估' }}
          </button>
        </div>
      </div>

      <div v-if="evaluationResults.length > 0" class="section">
        <h3>评估结果</h3>
        <div class="results-list">
          <div v-for="result in evaluationResults" :key="result.id" class="result-card">
            <div class="result-header">
              <div class="result-info">
                <span class="result-label">训练ID：</span>{{ result.trainingId }}
              </div>
              <div class="result-info">
                <span class="result-label">评估时间：</span>{{ result.evaluatedAt }}
              </div>
            </div>
            <div class="result-metrics">
              <div v-if="result.metrics.accuracy !== null" class="metric-item">
                <span class="metric-label">准确率：</span>
                <span class="metric-value">{{ (result.metrics.accuracy * 100).toFixed(2) }}%</span>
              </div>
              <div v-if="result.metrics.precision !== null" class="metric-item">
                <span class="metric-label">精确率：</span>
                <span class="metric-value">{{ (result.metrics.precision * 100).toFixed(2) }}%</span>
              </div>
              <div v-if="result.metrics.recall !== null" class="metric-item">
                <span class="metric-label">召回率：</span>
                <span class="metric-value">{{ (result.metrics.recall * 100).toFixed(2) }}%</span>
              </div>
              <div v-if="result.metrics.f1 !== null" class="metric-item">
                <span class="metric-label">F1分数：</span>
                <span class="metric-value">{{ (result.metrics.f1 * 100).toFixed(2) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTrainingRecords } from '../api/trainingRecords'

const trainingRecords = ref([])
const selectedRecord = ref(null)
const evaluating = ref(false)
const evaluationResults = ref([])

const testConfig = ref({
  dataset: 'test_set_1',
  metrics: {
    accuracy: true,
    precision: true,
    recall: false,
    f1: false
  },
  batchSize: 32
})

const completedRecords = computed(() => {
  return trainingRecords.value.filter(r => r.status === 'completed')
})

const selectRecord = (record) => {
  selectedRecord.value = record
}

const startEvaluation = async () => {
  if (!selectedRecord.value) return
  
  evaluating.value = true
  
  // 模拟评估过程
  setTimeout(() => {
    const result = {
      id: 'EVAL-' + Date.now(),
      trainingId: selectedRecord.value.id,
      evaluatedAt: new Date().toLocaleString('zh-CN'),
      metrics: {
        accuracy: testConfig.value.metrics.accuracy ? Math.random() * 0.2 + 0.8 : null,
        precision: testConfig.value.metrics.precision ? Math.random() * 0.2 + 0.75 : null,
        recall: testConfig.value.metrics.recall ? Math.random() * 0.2 + 0.7 : null,
        f1: testConfig.value.metrics.f1 ? Math.random() * 0.2 + 0.72 : null
      }
    }
    
    evaluationResults.value.unshift(result)
    evaluating.value = false
  }, 2000)
}

const loadTrainingRecords = async () => {
  try {
    const result = await getTrainingRecords()
    trainingRecords.value = result.data || []
  } catch (error) {
    console.error('加载训练记录失败:', error)
    trainingRecords.value = []
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

.evaluation-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.empty-message {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.record-item {
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.record-item:hover {
  border-color: #42b983;
  box-shadow: 0 2px 8px rgba(66, 185, 131, 0.2);
}

.record-item.selected {
  border-color: #42b983;
  background: #f0fdf4;
}

.record-id {
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
}

.record-time {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.record-status {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 4px;
  font-size: 0.85rem;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: bold;
  color: #555;
}

.form-group select,
.form-group input[type="number"] {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.checkbox-group {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  cursor: pointer;
}

.action-buttons {
  margin-top: 1.5rem;
  display: flex;
  gap: 1rem;
}

.start-eval-btn {
  padding: 0.75rem 2rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.start-eval-btn:hover:not(:disabled) {
  background: #359268;
}

.start-eval-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-card {
  background: #fafafa;
  padding: 1.5rem;
  border-radius: 6px;
  border-left: 4px solid #42b983;
}

.result-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.result-info {
  color: #555;
}

.result-label {
  font-weight: bold;
}

.result-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metric-item {
  padding: 0.75rem;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.metric-label {
  font-weight: bold;
  color: #666;
  display: block;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.5rem;
  color: #42b983;
  font-weight: bold;
}
</style>
