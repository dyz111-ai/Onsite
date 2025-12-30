<template>
  <div class="auth-container">
    <div class="auth-wrapper">
      <!-- 左侧图片区域 -->
      <div class="left-section">
        <div class="brand-section">
          <h1 class="brand-title">Onsite测训一体平台</h1>

        </div>
        <div class="illustration">
          <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
            <!-- 背景装饰 -->
            <circle cx="200" cy="150" r="120" fill="#667eea" opacity="0.1"/>
            <circle cx="200" cy="150" r="90" fill="#764ba2" opacity="0.1"/>
            
            <!-- 自动驾驶汽车 -->
            <!-- 车身 -->
            <rect x="120" y="140" width="160" height="60" rx="8" fill="#667eea"/>
            <!-- 车窗 -->
            <path d="M 140 140 L 160 120 L 220 120 L 240 140 Z" fill="#764ba2"/>
            <rect x="145" y="125" width="30" height="15" fill="#e0e7ff"/>
            <rect x="185" y="125" width="30" height="15" fill="#e0e7ff"/>
            
            <!-- 车灯 -->
            <circle cx="130" cy="160" r="6" fill="#fff" opacity="0.9"/>
            <circle cx="270" cy="160" r="6" fill="#fff" opacity="0.9"/>
            
            <!-- 车轮 -->
            <circle cx="150" cy="200" r="20" fill="#333"/>
            <circle cx="150" cy="200" r="12" fill="#666"/>
            <circle cx="250" cy="200" r="20" fill="#333"/>
            <circle cx="250" cy="200" r="12" fill="#666"/>
            
            <!-- 传感器/雷达波 -->
            <circle cx="200" cy="110" r="8" fill="#764ba2"/>
            <circle cx="200" cy="110" r="15" fill="none" stroke="#764ba2" stroke-width="2" opacity="0.6"/>
            <circle cx="200" cy="110" r="22" fill="none" stroke="#764ba2" stroke-width="2" opacity="0.3"/>
            
            <!-- 道路线 -->
            <line x1="50" y1="220" x2="100" y2="220" stroke="#667eea" stroke-width="4" stroke-dasharray="10,5" opacity="0.4"/>
            <line x1="300" y1="220" x2="350" y2="220" stroke="#667eea" stroke-width="4" stroke-dasharray="10,5" opacity="0.4"/>
            
            <!-- AI标识 -->
            <text x="190" y="175" font-size="20" font-weight="bold" fill="#fff">AI</text>
            
            <!-- 装饰元素 -->
            <circle cx="80" cy="80" r="8" fill="#667eea" opacity="0.6"/>
            <circle cx="320" cy="100" r="12" fill="#764ba2" opacity="0.6"/>
            <circle cx="100" cy="240" r="6" fill="#667eea" opacity="0.6"/>
            <circle cx="300" cy="240" r="10" fill="#764ba2" opacity="0.6"/>
            
            <!-- 数据流动效果 -->
            <path d="M 60 150 Q 80 140 100 150" fill="none" stroke="#667eea" stroke-width="2" opacity="0.5"/>
            <path d="M 300 150 Q 320 140 340 150" fill="none" stroke="#764ba2" stroke-width="2" opacity="0.5"/>
          </svg>
        </div>
      </div>
      
      <!-- 右侧登录表单 -->
      <div class="right-section">
        <div class="auth-card">
          <h2>{{ isLogin ? '欢迎回来' : '创建账号' }}</h2>
          <p class="auth-description">{{ isLogin ? '登录以继续使用平台' : '注册新账号开始使用' }}</p>
          
          <!-- 用户/管理员切换 -->
          <div v-if="isLogin" class="role-switch">
            <button 
              :class="['role-btn', { active: loginRole === 'user' }]"
              @click="loginRole = 'user'"
            >
              
              用户登录
            </button>
            <button 
              :class="['role-btn', { active: loginRole === 'admin' }]"
              @click="loginRole = 'admin'"
            >
              
              管理员登录
            </button>
          </div>
          
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label>{{ loginRole === 'admin' ? '账号' : '用户名' }}</label>
              <div class="input-wrapper">
                <span class="input-icon">👤</span>
                <input 
                  v-model="form.username" 
                  type="text" 
                  :placeholder="loginRole === 'admin' ? '请输入管理员账号' : '请输入用户名'"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label>密码</label>
              <div class="input-wrapper">
                <span class="input-icon">🔒</span>
                <input 
                  v-model="form.password" 
                  type="password" 
                  placeholder="请输入密码"
                  required
                />
              </div>
            </div>

            <div v-if="!isLogin" class="form-group">
              <label>确认密码</label>
              <div class="input-wrapper">
                <span class="input-icon">🔒</span>
                <input 
                  v-model="form.confirmPassword" 
                  type="password" 
                  placeholder="请再次输入密码"
                  required
                />
              </div>
            </div>

            <div v-if="error" class="error-message">{{ error }}</div>

            <button type="submit" class="submit-btn" :disabled="loading">
              <span v-if="loading" class="loading-spinner-small"></span>
              {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
            </button>
          </form>

          <div v-if="loginRole === 'user'" class="switch-mode">
            <span v-if="isLogin">
              还没有账号？
              <a @click="isLogin = false">立即注册</a>
            </span>
            <span v-else>
              已有账号？
              <a @click="isLogin = true">立即登录</a>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, register, adminLogin } from '../api/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const isLogin = ref(true)
    const loginRole = ref('user')
    const loading = ref(false)
    const error = ref('')
    
    const form = ref({
      username: '',
      password: '',
      confirmPassword: ''
    })

    const handleSubmit = async () => {
      error.value = ''
      
      // 验证
      if (!isLogin.value) {
        if (form.value.password !== form.value.confirmPassword) {
          error.value = '两次输入的密码不一致'
          return
        }
        if (form.value.password.length < 6) {
          error.value = '密码长度至少为6位'
          return
        }
      }

      loading.value = true

      try {
        let response
        
        if (loginRole.value === 'admin') {
          // 管理员登录
          response = await adminLogin({
            account: form.value.username,
            password: form.value.password
          })
          
          // 保存 token 和管理员信息
          localStorage.setItem('token', response.token)
          localStorage.setItem('user', JSON.stringify(response.admin))
          
          // 跳转到管理员页面
          router.push('/admin')
        } else {
          // 用户登录/注册
          if (isLogin.value) {
            response = await login({
              username: form.value.username,
              password: form.value.password
            })
          } else {
            response = await register({
              username: form.value.username,
              password: form.value.password
            })
          }

          // 保存 token 和用户信息
          localStorage.setItem('token', response.token)
          localStorage.setItem('user', JSON.stringify(response.user))

          // 跳转到比赛页面
          router.push('/competition')
        }
      } catch (err) {
        error.value = err.response?.data?.error || '操作失败，请重试'
      } finally {
        loading.value = false
      }
    }

    return {
      isLogin,
      loginRole,
      form,
      error,
      loading,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.auth-wrapper {
  display: flex;
  width: 100%;
  max-width: 1200px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  min-height: 600px;
}

/* 左侧区域 */
.left-section {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 3rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  position: relative;
}

.brand-section {
  text-align: center;
  margin-bottom: 3rem;
  z-index: 1;
}

.brand-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.brand-subtitle {
  font-size: 1.1rem;
  opacity: 0.95;
  letter-spacing: 2px;
}

.illustration {
  width: 100%;
  max-width: 400px;
  z-index: 1;
}

.illustration svg {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.2));
}

/* 右侧区域 */
.right-section {
  flex: 1;
  padding: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
}

.auth-card {
  width: 100%;
  max-width: 400px;
}

h2 {
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

.auth-description {
  color: #666;
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.role-switch {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.role-btn {
  flex: 1;
  padding: 0.875rem;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.role-icon {
  font-size: 1.2rem;
}

.role-btn:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.role-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
  font-size: 0.95rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  font-size: 1.2rem;
  pointer-events: none;
  z-index: 1;
  filter: grayscale(100%) brightness(0);
}

.form-group input {
  width: 100%;
  padding: 0.875rem 0.875rem 0.875rem 3rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.error-message {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  padding: 0.875rem;
  background: #fee;
  border-radius: 8px;
  border-left: 4px solid #e74c3c;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.switch-mode {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
  font-size: 0.95rem;
}

.switch-mode a {
  color: #667eea;
  cursor: pointer;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s;
}

.switch-mode a:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 968px) {
  .auth-wrapper {
    flex-direction: column;
  }
  
  .left-section {
    padding: 2rem;
    min-height: 300px;
  }
  
  .brand-title {
    font-size: 2rem;
  }
  
  .illustration {
    max-width: 300px;
  }
  
  .right-section {
    padding: 2rem;
  }
}
</style>
