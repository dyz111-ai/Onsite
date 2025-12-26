<template>
  <div class="task-submit-view">
    <h2>任务提交</h2>
    <div class="control-panel">
      <button @click="showSubmitDialog" class="submit-btn">
        任务提交
      </button>
    </div>

    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

    <!-- 任务列表 -->
    <div v-if="taskList.length > 0" class="tasks-section">
      <h3>任务列表</h3>
      <div class="tasks-container">
        <div class="tasks-list">
          <div v-for="task in taskList" :key="task.id" class="task-card">
            <div class="task-info">
              <div class="task-id">
                <strong>任务ID：</strong>{{ task.id }}
              </div>
              <div class="task-time">
                <strong>创建时间：</strong>{{ task.createdAt }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 任务提交弹窗 -->
    <div v-if="showDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>任务提交</h3>
          <button class="close-btn" @click="closeDialog">×</button>
        </div>
        <div class="dialog-body">
          <!-- 弹窗内容留白 -->
        </div>
        <div class="dialog-footer">
          <button @click="closeDialog" class="cancel-btn">取消</button>
          <button @click="submitTask" class="confirm-btn">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTaskList, createTask } from '../api/taskSubmit'

const showDialog = ref(false)
const taskList = ref([])
const message = ref('')
const messageType = ref('info')

// 从服务器加载任务列表
const loadTasks = async () => {
  try {
    const result = await getTaskList()
    taskList.value = result.data || []
  } catch (error) {
    message.value = '加载任务列表失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
    taskList.value = []
  }
}

const showSubmitDialog = () => {
  showDialog.value = true
}

const closeDialog = () => {
  showDialog.value = false
}

const submitTask = async () => {
  // 生成任务记录
  const newTask = {
    id: 'TASK-' + Date.now(),
    createdAt: new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }
  
  try {
    await createTask(newTask)
    // 重新加载任务列表
    await loadTasks()
    message.value = '任务创建成功'
    messageType.value = 'success'
    closeDialog()
  } catch (error) {
    message.value = '创建任务失败：' + (error.response?.data?.error || error.message)
    messageType.value = 'error'
  }
}

// 组件挂载时加载任务列表
onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.task-submit-view {
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

.submit-btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
  background: #9c27b0;
  color: white;
}

.submit-btn:hover {
  background: #7b1fa2;
}

.tasks-section {
  margin-bottom: 2rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.tasks-container {
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

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.task-card {
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

.task-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.task-info {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.task-id,
.task-time {
  color: #555;
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

