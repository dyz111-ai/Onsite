<template>
  <div class="render-list-view">
    <div class="header">
      <h2>渲染数据集列表</h2>
      <div class="header-actions">
        <button @click="showTaskSubmitModal = true" class="submit-btn">
          提交新任务
        </button>
      </div>
    </div>

    <!-- Task Submit Modal -->
    <div v-if="showTaskSubmitModal" class="modal-overlay" @click="closeTaskSubmitModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>提交新任务</h3>
          <button class="close-btn" @click="closeTaskSubmitModal">×</button>
        </div>
        <div class="modal-body">
          <TaskSubmittingComponent 
            @close="closeTaskSubmitModal" 
            @success="onTaskSubmitSuccess"
          />
        </div>
      </div>
    </div>

    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 渲染列表 -->
    <div v-else-if="renderRecords.length > 0" class="render-list-section">
      <div class="list-info">
        共 {{ renderRecords.length }} 个渲染数据集
      </div>
      
      <div class="render-cards">
        <div v-for="render in renderRecords" :key="render.render_id" class="render-card">
          <div class="render-card-header">
            <div class="render-id">
              <strong>渲染ID：</strong>{{ render.render_id }}
            </div>
            <div class="render-status">
              <span :class="['status-badge', getStatusClass(render.status)]">
                {{ render.status }}
              </span>
            </div>
          </div>
          
          <div class="render-card-body">
            <div class="render-field">
              <strong>名称：</strong>
              <span class="render-name">{{ render.name || '未命名' }}</span>
            </div>
            
            <div class="render-field">
              <strong>创建时间：</strong>
              <span class="render-time">{{ formatTime(render.created_time) }}</span>
            </div>
            
            <div class="render-field">
              <strong>资源消耗：</strong>
              <span class="render-time">{{ formatTime(render.render_cost) }}</span>
            </div>
            
            <div v-if="render.description" class="render-field">
              <strong>描述：</strong>
              <span class="render-description">{{ render.description }}</span>
            </div>
            
            <div v-if="render.file_count !== undefined" class="render-field">
              <strong>文件数量：</strong>
              <span class="render-count">{{ render.file_count }} 个</span>
            </div>
            
            <div v-if="render.size !== undefined" class="render-field">
              <strong>数据大小：</strong>
              <span class="render-size">{{ formatSize(render.size) }}</span>
            </div>
          </div>
          
          <div class="render-card-footer">
            <button @click="previewVideo(render.render_id)" class="video-btn">
              预览视频
            </button>
            <button v-if="allowDelete" @click="deleteRender(render.render_id)" class="delete-btn">
              删除
            </button>
            <!-- New download button - only show for completed renders -->
            <button 
              v-if="render.status === 'Completed'" 
              @click="downloadDataset(render.render_id)" 
              :disabled="downloading[render.render_id]"
              class="download-btn"
            >
              {{ downloading[render.render_id] ? '下载中...' : '下载' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">📁</div>
      <p>暂无渲染数据集</p>
      <p class="empty-hint">创建一个渲染数据集以开始使用</p>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showDetailDialog" class="dialog-overlay" @click="closeDetailDialog">
      <div class="dialog-content detail-dialog" @click.stop>
        <div class="dialog-header">
          <h3>渲染数据集详情 - ID: {{ currentDetailId }}</h3>
          <button class="close-btn" @click="closeDetailDialog">×</button>
        </div>
        <div class="dialog-body">
          <div v-if="detailLoading" class="loading">加载中...</div>
          <div v-else-if="detailError" class="error-message">{{ detailError }}</div>
          <div v-else class="detail-content">
            <div class="detail-section">
              <h4>基本信息</h4>
              <div class="detail-field">
                <strong>渲染ID：</strong>{{ detailData.render_id }}
              </div>
              <div class="detail-field">
                <strong>名称：</strong>{{ detailData.name || '未命名' }}
              </div>
              <div class="detail-field">
                <strong>状态：</strong>
                <span :class="['status-badge', getStatusClass(detailData.status)]">
                  {{ detailData.status }}
                </span>
              </div>
              <div class="detail-field">
                <strong>创建时间：</strong>{{ formatTime(detailData.created_time) }}
              </div>
              <div class="detail-field">
                <strong>更新时间：</strong>{{ formatTime(detailData.updated_time) }}
              </div>
              <div v-if="detailData.description" class="detail-field">
                <strong>描述：</strong>{{ detailData.description }}
              </div>
            </div>
            
            <div v-if="detailData.file_count !== undefined" class="detail-section">
              <h4>数据统计</h4>
              <div class="detail-field">
                <strong>文件数量：</strong>{{ detailData.file_count }} 个
              </div>
              <div v-if="detailData.size" class="detail-field">
                <strong>数据大小：</strong>{{ formatSize(detailData.size) }}
              </div>
            </div>
            
            <div v-if="detailData.config" class="detail-section">
              <h4>配置信息</h4>
              <pre class="config-code">{{ JSON.stringify(detailData.config, null, 2) }}</pre>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="closeDetailDialog" class="cancel-btn">关闭</button>
        </div>
      </div>
    </div>
    <!-- Video Preview Overlay -->
<div v-if="currentVideoId" class="video-preview-overlay" @click="closeVideoPreview">
  <div class="video-preview-content" @click.stop>
    <div class="video-preview-header">
      <h3>视频预览 - ID: {{ currentVideoId }}</h3>
      <button @click="closeVideoPreview" class="close-btn">×</button>
    </div>
    <div class="video-preview-body">
      <VideoComponent 
        :taskId="currentVideoId" 
        taskType="render"
      />
    </div>
  </div>
</div>
  </div>
</template>
<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue'
import axios from 'axios'
import TaskSubmittingComponent from '../components/TaskSubmittingComponent.vue' // Import the component
import VideoComponent from '../components/VideoComponent.vue'

const props = defineProps({
  // 是否允许多选
  multiple: {
    type: Boolean,
    default: true
  },
  // 是否显示选择按钮
  showSelect: {
    type: Boolean,
    default: true
  },
  // 是否允许删除
  allowDelete: {
    type: Boolean,
    default: false
  },
  // 初始选中的渲染ID数组
  selectedIds: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['select', 'delete', 'refresh'])

const renderRecords = ref([])
const loading = ref(false)
const message = ref('')
const messageType = ref('info')

// Task Submit Modal State
const showTaskSubmitModal = ref(false)

// 详情弹窗相关
const showDetailDialog = ref(false)
const currentDetailId = ref(null)
const detailData = ref({})
const detailLoading = ref(false)
const detailError = ref('')

// Track currently previewed video
const currentVideoId = ref(null)

// Track download states for each render ID
const downloading = ref({})

// Download dataset archive
const downloadDataset = async (renderId) => {
  // 构建前端文件路径 - 直接访问public目录下的文件
  console.log('下载文件:', renderId)
  const downloadUrl = `/cache/render/dataset/${renderId}.tar.gz`;
  
  // 创建一个临时的a标签用于下载
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = `${renderId}.tar.gz`;
  link.style.display = 'none';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
// 加载渲染列表
const loadRenderRecords = async () => {
  loading.value = true
  message.value = ''
  
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/render/records', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    renderRecords.value = response.data.data || []
    
    if (renderRecords.value.length === 0) {
      message.value = '暂无渲染数据集'
      messageType.value = 'info'
    }
  } catch (error) {
    console.error('加载渲染数据集失败:', error)
    message.value = '加载渲染数据集失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
    renderRecords.value = []
  } finally {
    loading.value = false
  }
}

// 刷新列表
const refreshList = () => {
  loadRenderRecords()
  emit('refresh')
}

// Open video preview
const previewVideo = (renderId) => {
  currentVideoId.value = renderId
}

// Close video preview
const closeVideoPreview = () => {
  currentVideoId.value = null
}
// 关闭详情弹窗
const closeDetailDialog = () => {
  showDetailDialog.value = false
  currentDetailId.value = null
  detailData.value = {}
}

// 选择渲染数据集
const selectRender = (render) => {
  emit('select', render)
}

// 删除渲染数据集
const deleteRender = async (renderId) => {
  if (!confirm('确定要删除这个渲染数据集吗？删除后无法恢复。')) {
    return
  }
  
  try {
    const token = localStorage.getItem('token')
    await axios.delete(`/api/render/records/${renderId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    message.value = '删除成功'
    messageType.value = 'success'
    
    // 从列表中移除
    renderRecords.value = renderRecords.value.filter(r => r.render_id !== renderId)
    
    // 通知父组件
    emit('delete', renderId)
  } catch (error) {
    console.error('删除失败:', error)
    message.value = '删除失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
  }
}

// 打开任务提交模态框
const openTaskSubmitModal = () => {
  showTaskSubmitModal.value = true
}

// 关闭任务提交模态框
const closeTaskSubmitModal = () => {
  showTaskSubmitModal.value = false
}

// 任务提交成功后的回调
const onTaskSubmitSuccess = () => {
  message.value = '任务提交成功！'
  messageType.value = 'success'
  refreshList()
  // Optionally refresh the list or update UI
  setTimeout(() => {
    closeTaskSubmitModal()
  }, 1500)
}

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return '-'
  
  try {
    const date = new Date(timeString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  } catch (e) {
    return timeString
  }
}

// 格式化文件大小
const formatSize = (bytes) => {
  if (bytes === undefined || bytes === null) return '-'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`
}

// 获取状态样式类
const getStatusClass = (status) => {
  const statusMap = {
    'completed': 'status-completed',
    'processing': 'status-processing',
    'pending': 'status-pending',
    'failed': 'status-failed'
  }
  return statusMap[status?.toLowerCase()] || 'status-default'
}

onMounted(() => {
  loadRenderRecords()
})
</script>
<style scoped>
.render-list-view {
  padding: 1.5rem;
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header h2 {
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.submit-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #42b983;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  background: white;
  color: #42b983;
  transition: all 0.3s;
}

.submit-btn:hover {
  background: #42b983;
  color: white;
}

.refresh-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #9c27b0;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  background: white;
  color: #9c27b0;
  transition: all 0.3s;
}

.refresh-btn:hover {
  background: #9c27b0;
  color: white;
}

/* Modal styles */
.modal-overlay {
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

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.25rem;
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

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.message {
  padding: 0.75rem 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
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
  padding: 4rem;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #9c27b0;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.list-info {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.render-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.render-card {
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s, transform 0.3s;
  overflow: hidden;
}

.render-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.render-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: #fafafa;
  border-bottom: 1px solid #eee;
}

.render-id {
  font-size: 0.85rem;
  color: #666;
  font-family: 'Courier New', monospace;
}

.render-status {
  flex-shrink: 0;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-processing {
  background: #fff3e0;
  color: #f57c00;
}

.status-pending {
  background: #e3f2fd;
  color: #1976d2;
}

.status-failed {
  background: #ffebee;
  color: #c62828;
}

.status-default {
  background: #f5f5f5;
  color: #666;
}

.render-card-body {
  padding: 1.25rem;
}

.render-field {
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
  line-height: 1.4;
}

.render-field:last-child {
  margin-bottom: 0;
}

.render-field strong {
  color: #555;
  min-width: 70px;
  display: inline-block;
}

.render-name {
  color: #333;
  font-weight: 500;
}

.render-time {
  color: #666;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
}

.render-description {
  color: #666;
  line-height: 1.5;
}

.render-count,
.render-size {
  color: #9c27b0;
  font-weight: 500;
}

.render-card-footer {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  background: #fafafa;
  border-top: 1px solid #eee;
}

.detail-btn,
.select-btn,
.delete-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.3s;
  flex: 1;
}

.detail-btn {
  background: #3498db;
  color: white;
}

.detail-btn:hover {
  background: #2980b9;
}

.select-btn {
  background: #42b983;
  color: white;
}

.select-btn:hover {
  background: #359268;
}

.delete-btn {
  background: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background: #c0392b;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-hint {
  font-size: 0.9rem;
  color: #999;
  margin-top: 0.5rem;
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
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.dialog-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.25rem;
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
  flex: 1;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #eee;
  flex-shrink: 0;
}

.cancel-btn {
  padding: 0.5rem 1.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #333;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

.detail-dialog {
  max-width: 800px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-section {
  background: #fafafa;
  padding: 1.25rem;
  border-radius: 6px;
  border: 1px solid #eee;
}

.detail-section h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.detail-field {
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
  line-height: 1.5;
}

.detail-field:last-child {
  margin-bottom: 0;
}

.detail-field strong {
  color: #555;
  min-width: 80px;
  display: inline-block;
}

.config-code {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 1rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  overflow-x: auto;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}

.loading,
.error-message {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error-message {
  color: #e74c3c;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .render-cards {
    grid-template-columns: 1fr;
  }
  
  .render-card-footer {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .detail-btn,
  .select-btn,
  .delete-btn {
    width: 100%;
  }
  
  .dialog-content {
    width: 95%;
    max-height: 95vh;
  }
  
  .header-actions {
    flex-direction: column;
  }
  
  .submit-btn,
  .refresh-btn {
    width: 100%;
  }
}

/* Video Preview Overlay */
.video-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.video-preview-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.video-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #eee;
  background: #f8f8f8;
}

.video-preview-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.25rem;
}

.video-preview-body {
  padding: 1.5rem;
  overflow: auto;
  flex: 1;
  display: flex;
  justify-content: center;
}

.video-btn {
  background: #3498db;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.3s;
  flex: 1;
}

.video-btn:hover {
  background: #2980b9;
}

.download-btn {
  background: #3f51b5;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.3s;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.download-btn:hover:not([disabled]) {
  background: #303f9f;
  transform: translateY(-1px);
}

.download-btn:disabled {
  background: #b3c1dc;
  cursor: not-allowed;
  transform: none;
}
</style>