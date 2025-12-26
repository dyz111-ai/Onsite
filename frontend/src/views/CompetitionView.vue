<template>
  <div class="competition-view">
    <h2>赛题查看</h2>
    
    <!-- 赛题列表 -->
    <div v-if="competitionList.length > 0" class="competition-section">
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>赛题编号</th>
              <th>场景下载</th>
              <th>预览场景</th>
              <th>截止时间</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in competitionList" :key="index">
              <td>{{ item.id }}</td>
              <td>
                <button @click="handleDownload(item)" class="action-btn download-btn">
                  {{ item.download }}
                </button>
              </td>
              <td>
                <button @click="handlePreview(item)" class="action-btn preview-btn">
                  {{ item.preview }}
                </button>
              </td>
              <td>{{ item.deadline }}</td>
              <td>
                <span :class="['status-badge', getStatusClass(item.status)]">
                  {{ item.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div v-else class="empty-state">
      暂无赛题数据
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCompetitionList } from '../api/competition'

const competitionList = ref([])

// 加载赛题列表
const loadCompetitions = async () => {
  try {
    const result = await getCompetitionList()
    competitionList.value = result.data || []
  } catch (error) {
    console.error('加载赛题列表失败:', error)
    competitionList.value = []
  }
}

// 处理下载点击
const handleDownload = (item) => {
  // 后续会添加下载逻辑
  console.log('下载赛题:', item.id)
}

// 处理预览点击
const handlePreview = (item) => {
  // 后续会添加预览逻辑
  console.log('预览赛题:', item.id)
}

// 获取状态样式类
const getStatusClass = (status) => {
  if (status === '正常') {
    return 'status-normal'
  } else if (status === '已截止') {
    return 'status-expired'
  } else if (status === '即将截止') {
    return 'status-warning'
  }
  return ''
}

onMounted(() => {
  loadCompetitions()
})
</script>

<style scoped>
.competition-view {
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

.competition-section {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 1.5rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow-x: auto;
}

table {
  width: 100%;
  max-width: 100%;
  border-collapse: collapse;
  background: white;
  min-width: 100%;
}

thead {
  background: #f5f5f5;
}

th,
td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
  font-size: 0.9rem;
  word-wrap: break-word;
  white-space: nowrap;
}

th:first-child,
td:first-child {
  width: 20%;
}

th:nth-child(2),
td:nth-child(2),
th:nth-child(3),
td:nth-child(3) {
  width: 18%;
}

th:nth-child(4),
td:nth-child(4) {
  width: 20%;
}

th:nth-child(5),
td:nth-child(5) {
  width: 15%;
}

th {
  font-weight: bold;
  color: #555;
}

tbody tr:hover {
  background: #f9f9f9;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
}

.download-btn {
  background: #3498db;
  color: white;
}

.download-btn:hover {
  background: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.preview-btn {
  background: #42b983;
  color: white;
}

.preview-btn:hover {
  background: #359268;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-normal {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-expired {
  background: #ffebee;
  color: #c62828;
}

.status-warning {
  background: #fff3e0;
  color: #e65100;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
