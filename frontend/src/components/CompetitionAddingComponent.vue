<template>
  <div class="competition-adding-container">
    <div class="form-group">
      <label for="type">赛题类型:</label>
      <!-- Changed from input to select dropdown -->
      <select 
        id="type" 
        v-model="formData.type" 
        @change="onTypeChange"
        required
        :disabled="loadingMinNumber || submitting"
      >
        <option value="" disabled selected>请选择赛题类型</option>
        <option value="A">A卷</option>
        <option value="B">B卷</option>
        <option value="C">C卷</option>
      </select>
    </div>
    
    <div class="form-group">
      <label for="number">题号:</label>
      <div class="input-with-hint">
        <!-- 使用 disabled 替代 readonly 以获得更明确的视觉反馈 -->
        <input 
          type="text" 
          id="number" 
          :value="formData.number" 
          :placeholder="loadingMinNumber ? '加载中...' : '系统自动生成'"
          required
          disabled
          class="disabled-input no-spinner"
        >
        <div v-if="minNumberForType !== null && !loadingMinNumber" class="hint">
          系统已自动设置为: {{ formData.number }}
        </div>
        <!-- 添加加载状态提示 -->
        <div v-if="loadingMinNumber" class="hint loading">
          正在生成题号...
        </div>
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
  name: 'CompetitionAddingComponent',
  data() {
    return {
      showSuccess: false,
      formData: {
        type: '',
        number: ''
      },
      minNumberForType: null,
      loadingMinNumber: false,
      submitting: false,
      openScenarioFile: null,
      targetPointsFile: null
    }
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
    
    async onTypeChange() {
      if (!this.formData.type) return;
      
      this.loadingMinNumber = true;
      const typeValue = `Type${this.formData.type}`;
      
      try {
        const response = await fetch(`/api/competition/get-mini-number/${typeValue}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const result = await response.json();
          this.minNumberForType = result.min_number !== undefined ? result.min_number : 0;
          this.formData.number = this.minNumberForType + 1;
        } else {
          // If no competitions of this type exist yet, start with 1
          this.minNumberForType = 0;
          this.formData.number = 1;
        }
      } catch (error) {
        console.error("获取最小题号失败:", error);
        this.minNumberForType = 0;
        this.formData.number = 1;
      } finally {
        this.loadingMinNumber = false;
      }
    },
    
    async submitCompetition() {
      // Enhanced validation
      if (!this.formData.type || !this.formData.number || 
          !this.openScenarioFile || !this.targetPointsFile) {
        alert('请填写所有必填字段');
        return;
      }
      
      this.submitting = true;
      
      try {
        // Format dates
        const createdTime = new Date().toISOString().split('T')[0];
        const endTime = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        const typeValue = `Type${this.formData.type}`;
        
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('created_time', createdTime);
        formData.append('end_time', endTime);
        formData.append('status', 'Unreleased');
        formData.append('type', typeValue);
        formData.append('number', parseInt(this.formData.number));
        formData.append('open_scenario', this.openScenarioFile);
        formData.append('target_points', this.targetPointsFile);
        
        const response = await fetch('/api/competition/add', {
          method: 'POST',
          body: formData
          // No Content-Type header needed - browser sets it automatically
        });
        
        // Process response (same as existing logic)
        if (response.ok) {
          this.showSuccess = true;
          setTimeout(() => {
            this.showSuccess = false;
          }, 3000);
          this.$emit('success');
        } else {
          // Error handling (same as existing logic)
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