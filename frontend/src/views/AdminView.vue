<template>
  <div class="admin-content">
    <h1>赛题管理</h1>
    
    <!-- Add competition button -->
    <button class="add-btn" @click="openModal">
      添加新赛题
    </button>
    
    <!-- Competition list section -->
    <div class="competition-list-container">
      <!-- Type selector -->
      <div class="form-group">
        <label for="competitionType">赛题类型:</label>
        <select 
          id="competitionType" 
          v-model="selectedListType" 
          @change="onListTypeChange"
          :disabled="loading"
        >
          <option value="" disabled selected>请选择赛题类型</option>
          <option value="A">A卷</option>
          <option value="B">B卷</option>
          <option value="C">C卷</option>
        </select>
      </div>
      
      <!-- Loading indicator -->
      <div v-if="loading" class="loading-indicator">
        <div class="spinner"></div>
        <span>加载赛题数据中...</span>
      </div>
      
      <!-- Error message -->
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="fetchCompetitions" class="retry-btn" :disabled="loading">重试</button>
      </div>
      
      <!-- Competition table -->
      <table v-if="!loading && competitions.length > 0" class="competition-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>创建时间</th>
            <th>结束时间</th>
            <th>状态</th>
            <th>类型</th>
            <th>题号</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="comp in competitions" :key="comp.id">
            <td>{{ comp.id }}</td>
            <td>{{ formatDate(comp.created_time) }}</td>
            <td>{{ formatDate(comp.end_time) }}</td>
            <td>
              <span class="status-badge" :class="statusClass(comp.status)">
                {{ formatStatus(comp.status) }}
              </span>
            </td>
            <td>{{ comp.type }}</td>
            <td>{{ comp.number }}</td>
            <td>
              <button class="view-btn" @click="viewCompetition(comp)">查看详情</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Empty state -->
      <div v-if="!loading && competitions.length === 0" class="empty-state">
        <p>暂无赛题数据</p>
      </div>
      
      <!-- Pagination -->
      <div v-if="competitions.length > 0" class="pagination">
        <button 
          :disabled="currentPage === 1" 
          @click="currentPage--"
          class="pagination-btn"
        >
          上一页
        </button>
        <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        <button 
          :disabled="currentPage === totalPages" 
          @click="currentPage++"
          class="pagination-btn"
        >
          下一页
        </button>
      </div>
    </div>
    
    <!-- Competition modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>提交新赛题</h2>
        <CompetitionAddingComponent 
          @close="closeModal" 
          @success="onCompetitionAdded" 
        />
      </div>
    </div>
    
    <!-- Success message -->
    <div v-if="showSuccess" class="success-message">
      赛题提交成功！
    </div>
  </div>
</template>

<script>
import CompetitionAddingComponent from '../components/CompetitionAddingComponent.vue';

export default {
  name: 'AdminView',
  components: {
    CompetitionAddingComponent
  },
  data() {
    return {
      showModal: false,
      showSuccess: false,
      // New properties for competition list
      competitions: [],
      loading: false,
      error: null,
      currentPage: 1,
      itemsPerPage: 10,
      // For viewing competition details
      selectedCompetition: null,
      // New property for list type selection
      selectedListType: ''
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.competitions.length / this.itemsPerPage)
    },
    paginatedCompetitions() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.competitions.slice(start, end)
    }
  },
  mounted() {
    // Load competitions for default type or all types
    // Optionally, you could set a default type here
    this.selectedListType = 'A'; // Default to A type
    this.fetchCompetitions();
  },
  methods: {
    async fetchCompetitions() {
      if (!this.selectedListType) {
        this.error = '请选择赛题类型';
        return;
      }
      
      this.loading = true;
      this.error = null;
      
      try {
        const typeValue = `Type${this.selectedListType}`;
        const response = await fetch(`/api/competition/get-by-type/${typeValue}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const result = await response.json();
          // If the API returns all competitions in 'competitions' field
          if (result.competitions) {
            this.competitions = result.competitions;
          } 
          // If the API returns competitions directly (some implementations)
          else if (Array.isArray(result)) {
            this.competitions = result;
          }
          // If the API returns a different structure
          else {
            this.competitions = [];
            console.error('Unexpected API response structure:', result);
          }
          
          this.currentPage = 1;
        } else {
          throw new Error('获取赛题数据失败');
        }
      } catch (error) {
        this.error = `无法加载赛题数据: ${error.message}`;
        console.error('Fetch competitions error:', error);
      } finally {
        this.loading = false;
      }
    },
    
    onListTypeChange() {
      this.fetchCompetitions();
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    },
    
    formatStatus(status) {
      const statusMap = {
        'Unreleased': '未发布',
        'Published': '已发布'
      };
      return statusMap[status] || status;
    },
    
    statusClass(status) {
      return {
        'status-unreleased': status === 'Unreleased',
        'status-published': status === 'Published'
      };
    },

    
    viewCompetition(competition) {
      this.selectedCompetition = competition;
      // In a real implementation, you might open a detail modal or navigate to a detail page
      alert(`查看赛题详情: ${competition.type} - ${competition.number}`);
    },
    
    openModal() {
      this.showModal = true;
    },
    
    closeModal() {
      this.showModal = false;
    },
    
    onCompetitionAdded() {
      this.closeModal();
      this.showSuccess = true;
      setTimeout(() => {
        this.showSuccess = false;
      }, 3000);
      // Refresh the competition list after successful submission
      this.fetchCompetitions();
    }
  }
}
</script>

<style scoped>
.admin-content {
  padding: 2rem;
}

h1 {
  color: #333;
  margin-bottom: 1rem;
}

.add-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  margin-bottom: 2rem;
  transition: background-color 0.3s;
}

.add-btn:hover {
  background-color: #45a049;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

select, input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.readonly-input {
  background-color: #f5f5f5;
  cursor: not-allowed;
  color: #666;
}

.input-with-hint {
  position: relative;
}

.hint {
  position: absolute;
  bottom: -1.5rem;
  left: 0;
  font-size: 0.8rem;
  color: #666;
  background: white;
  padding: 0 0.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-btn, .submit-btn {
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.cancel-btn {
  background-color: #e0e0e0;
  border: none;
}

.cancel-btn:hover {
  background-color: #d0d0d0;
}

.submit-btn {
  background-color: #2196F3;
  color: white;
  border: none;
}

.submit-btn:hover {
  background-color: #0b7dda;
}

.success-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: #4CAF50;
  color: white;
  padding: 1rem;
  border-radius: 4px;
  z-index: 1000;
  animation: fadeOut 3s forwards;
}

.file-upload {
  position: relative;
}

.file-name {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #4CAF50;
}

.competition-list-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 1.5rem;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.loading-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  color: #666;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
  margin-right: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: #ffebee;
  color: #b71c1c;
  padding: 1rem;
  border-radius: 4px;
  text-align: center;
}

.retry-btn {
  background: none;
  border: 1px solid #b71c1c;
  color: #b71c1c;
  padding: 0.2rem 0.5rem;
  margin-left: 0.5rem;
  cursor: pointer;
}

.competition-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.competition-table th {
  background-color: #f5f5f5;
  padding: 0.8rem;
  text-align: left;
  border-bottom: 2px solid #ddd;
}

.competition-table td {
  padding: 0.8rem;
  border-bottom: 1px solid #ddd;
}

.competition-table tr:hover {
  background-color: #f9f9f9;
}

.status-badge {
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
  font-size: 0.85rem;
}

.status-unreleased {
  background-color: #fff3e0;
  color: #e65100;
}

.status-published {
  background-color: #e3f2fd;
  color: #0d47a1;
}

.view-btn {
  background: #2196F3;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
}

.view-btn:hover {
  background: #0b7dda;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 1.5rem;
  gap: 1rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}
.pagination-btn {
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
}

@keyframes fadeOut {
  0% { opacity: 1; }
  70% { opacity: 1; }
  100% { opacity: 0; }
}
</style>