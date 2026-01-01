<template>
  <div class="competition-adding-container">    
    <div class="form-group">
      <label for="number">名字:</label>
      <div class="input">
        <input 
          type="text" 
          id="name" 
          v-model="formData.name" 
          required
          class="no-spinner"
        >
      </div>
    </div>

    <div class="form-group">
      <label for="openScenario">OpenSCEANRIO 文件:</label>
      <div class="file-upload">
        <input 
          type="file" 
          id="openScenario" 
          accept=".xosc"
          @change="handleOpenScenarioFileChange"
          required
          :disabled="submitting"
        >
        <div v-if="openScenarioFile" class="file-name">
          已选择: {{ openScenarioFile.name }}
        </div>
      </div>
    </div>

    <div class="form-group">
      <label for="targetPoints">目标点文件:</label>
      <div class="file-upload">
        <input 
          type="file" 
          id="targetPoints" 
          accept=".json"
          @change="handleTargetPointsFileChange"
          required
          :disabled="submitting"
        >
        <div v-if="targetPointsFile" class="file-name">
          已选择: {{ targetPointsFile.name }}
        </div>
      </div>
    </div>

    <div class="modal-actions">
      <button class="cancel-btn" @click="closeModal" :disabled="submitting">
        取消
      </button>
      <button class="submit-btn" @click="submitCompetition" :disabled="submitting">
        {{ submitting ? '提交中...' : '提交' }}
      </button>
    </div>
    
    <!-- Success message -->
    <div v-if="showSuccess" class="success-message">
      赛题提交成功！
    </div>
  </div>
</template>
<script>
export default {
  name: 'TaskSubmittingComponent', // Updated component name to match functionality
  data() {
    return {
      showSuccess: false,
      formData: {
        name: '' // Updated to match backend field
      },
      submitting: false,
      openScenarioFile: null,
      targetPointsFile: null
    }
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
    
    async submitCompetition() {
      // Enhanced validation
      if (!this.formData.name || !this.openScenarioFile || !this.targetPointsFile) {
        alert('请填写所有必填字段');
        return;
      }
      
      this.submitting = true;
      
      try {
        // Format dates
        const createdTime = new Date().toISOString(); // Using ISO format for consistency
        
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('user_id', this.getUserId()); // You need to implement this
        formData.append('status', 'Rendering'); // Default status
        formData.append('created_time', createdTime);
        formData.append('name', this.formData.name);
        formData.append('open_scenario', this.openScenarioFile);
        formData.append('target_points', this.targetPointsFile);
        
        const response = await fetch('/api/task-submit/submit', { // Updated API endpoint
          method: 'POST',
          body: formData
          // No Content-Type header needed - browser sets it automatically
        });
        
        // Process response
        if (response.ok) {
          const result = await response.json();
          console.log(result); // Log the response
          this.showSuccess = true;
          setTimeout(() => {
            this.showSuccess = false;
            this.closeModal(); // Close modal after success
          }, 3000);
          this.$emit('success');
        } else {
          // Error handling
          let errorMessage = '未知错误';
          try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorMessage;
          } catch {
            errorMessage = await response.text() || errorMessage;
          }
          alert(`提交失败: ${errorMessage}`);
        }
      } catch (error) {
        alert(`请求失败: ${error.message}`);
      } finally {
        this.submitting = false;
      }
    },

    handleOpenScenarioFileChange(event) {
      const file = event.target.files[0];
      if (file && file.name.endsWith('.xosc')) {
        this.openScenarioFile = file;
      } else {
        alert('请选择.xosc格式的文件');
        event.target.value = ''; // Clear selection
      }
    },
    
    handleTargetPointsFileChange(event) {
      const file = event.target.files[0];
      if (file && file.name.endsWith('.json')) {
        this.targetPointsFile = file;
      } else {
        alert('请选择.json格式的文件');
        event.target.value = ''; // Clear selection
      }
    },
    
    // Helper method to get user ID - you'll need to implement this based on your auth system
    getUserId() {
      // Implement your logic to get user ID from JWT token, session, or other auth mechanism
      // This is just a placeholder - replace with your actual implementation
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const user = JSON.parse(storedUser);
        return user.id || user.userId;
      }
      // Or get from JWT token if that's how you handle auth
      return 1; // Placeholder - replace with actual user ID retrieval
    }
  }
}
</script>

<style scoped>
.competition-adding-container {
  width: 100%;
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

@keyframes fadeOut {
  0% { opacity: 1; }
  70% { opacity: 1; }
  100% { opacity: 0; }
}
</style>