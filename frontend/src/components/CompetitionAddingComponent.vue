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
        <div v-if="openScenarioError" class="error-message">
          {{ openScenarioError }}
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
        <div v-if="targetPointsError" class="error-message">
          {{ targetPointsError }}
        </div>
      </div>
    </div>

    <div v-if="formError" class="form-error">
      {{ formError }}
    </div>

    <div class="modal-actions">
      <button class="cancel-btn" @click="closeModal" :disabled="submitting">
        取消
      </button>
      <button 
        class="submit-btn" 
        @click="submitCompetition" 
        :disabled="submitting || !isFormValid"
      >
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
      targetPointsFile: null,
      openScenarioError: '',
      targetPointsError: '',
      formError: ''
    }
  },
  computed: {
    isFormValid() {
      return this.formData.type && 
             this.formData.number && 
             this.openScenarioFile && 
             this.targetPointsFile && 
             !this.openScenarioError && 
             !this.targetPointsError;
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
      if (!this.isFormValid) {
        this.formError = '请填写所有必填字段';
        return;
      }
      
      this.formError = ''; // Clear any form errors
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
          this.formError = `提交失败: ${errorMessage}`;
        }
      } catch (error) {
        this.formError = `请求失败: ${error.message}`;
      } finally {
        this.submitting = false;
      }
    },

    handleOpenScenarioFileChange(event) {
      const file = event.target.files[0];
      this.openScenarioError = ''; // Clear previous error
      
      if (!file) return;
      
      if (!file.name.endsWith('.xosc')) {
        this.openScenarioError = '请选择.xosc格式的文件';
        event.target.value = '';
        return;
      }
      
      const reader = new FileReader();
      
      reader.onload = (e) => {
        const content = e.target.result;
        
        try {
          const parser = new DOMParser();
          const xmlDoc = parser.parseFromString(content, 'text/xml');
          
          // Check for XML parsing errors
          const parserError = xmlDoc.querySelector('parsererror');
          if (parserError) {
            this.openScenarioError = 'XML格式错误：' + parserError.textContent;
            event.target.value = '';
            return;
          }
          
          // Check for required elements in OpenSCENARIO
          const catalogLocations = xmlDoc.getElementsByTagName('CatalogLocations');
          const roadNetwork = xmlDoc.getElementsByTagName('RoadNetwork');
          const entities = xmlDoc.getElementsByTagName('Entities');
          const scenarioObjects = xmlDoc.getElementsByTagName('ScenarioObject');
          
          if (catalogLocations.length === 0 || roadNetwork.length === 0 || entities.length === 0) {
            this.openScenarioError = '文件格式错误：缺少必要的OpenSCENARIO结构';
            event.target.value = '';
            return;
          }
          
          // Check for hero object
          let hasHeroObject = false;
          for (let obj of scenarioObjects) {
            if (obj.getAttribute('name') === 'hero') {
              hasHeroObject = true;
              break;
            }
          }
          
          if (!hasHeroObject) {
            this.openScenarioError = '文件格式错误：未找到 <ScenarioObject name="hero"> 元素';
            event.target.value = '';
            return;
          }
          
          // If all validations pass, set the file
          this.openScenarioFile = file;
          console.log('OpenSCENARIO文件验证通过，已加载文件：', file.name);
          
        } catch (error) {
          console.error('XML解析错误:', error);
          this.openScenarioError = 'XML格式错误：无法解析文件内容';
          event.target.value = '';
        }
      };
      
      reader.onerror = () => {
        this.openScenarioError = '读取文件失败，请重试';
        event.target.value = '';
      };
      
      reader.readAsText(file);
    },
    
    handleTargetPointsFileChange(event) {
      const file = event.target.files[0];
      this.targetPointsError = ''; // Clear previous error
      
      if (!file) return;
      
      if (!file.name.endsWith('.json')) {
        this.targetPointsError = '请选择.json格式的文件';
        event.target.value = '';
        return;
      }
      
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const content = e.target.result;
          const jsonData = JSON.parse(content);
          
          // Validate JSON structure - check if it's an object with x, y, z properties
          if (typeof jsonData !== 'object' || jsonData === null || Array.isArray(jsonData)) {
            this.targetPointsError = 'JSON文件必须包含一个对象';
            event.target.value = '';
            return;
          }
          
          // Check if object has only x, y, z properties
          const keys = Object.keys(jsonData);
          if (keys.length !== 3) {
            this.targetPointsError = '对象必须只包含x, y, z三个属性';
            event.target.value = '';
            return;
          }
          
          // Check if all required properties exist
          if (!keys.includes('x') || !keys.includes('y') || !keys.includes('z')) {
            this.targetPointsError = '对象必须包含x, y, z三个属性';
            event.target.value = '';
            return;
          }
          
          // Check if x, y, z are numbers
          if (typeof jsonData.x !== 'number' || 
              typeof jsonData.y !== 'number' || 
              typeof jsonData.z !== 'number') {
            this.targetPointsError = 'x, y, z必须是数字';
            event.target.value = '';
            return;
          }
          
          // If all validations pass, set the file
          this.targetPointsFile = file;
          console.log('JSON文件验证通过，已加载文件：', file.name);
          
        } catch (error) {
          console.error('JSON解析错误:', error);
          this.targetPointsError = 'JSON格式错误：无法解析文件内容';
          event.target.value = '';
        }
      };
      
      reader.onerror = () => {
        this.targetPointsError = '读取文件失败，请重试';
        event.target.value = '';
      };
      
      reader.readAsText(file);
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

.submit-btn:hover:not(:disabled) {
  background-color: #0b7dda;
}

.submit-btn:disabled {
  background-color: #bbdefb;
  cursor: not-allowed;
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

.error-message {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #f44336; /* Red color for error messages */
  font-weight: 500;
}

.form-error {
  margin: 1rem 0;
  padding: 0.8rem;
  background-color: #ffebee;
  color: #f44336;
  border-radius: 4px;
  font-weight: 500;
  border-left: 4px solid #f44336;
}

@keyframes fadeOut {
  0% { opacity: 1; }
  70% { opacity: 1; }
  100% { opacity: 0; }
}
</style>