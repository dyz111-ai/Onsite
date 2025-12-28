<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>{{ isLogin ? '登录' : '注册' }}</h2>
      
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>用户名</label>
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="请输入用户名"
            required
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码"
            required
          />
        </div>

        <div v-if="!isLogin" class="form-group">
          <label>确认密码</label>
          <input 
            v-model="form.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            required
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>

      <div class="switch-mode">
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
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, register } from '../api/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const isLogin = ref(true)
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
      } catch (err) {
        error.value = err.response?.data?.error || '操作失败，请重试'
      } finally {
        loading.value = false
      }
    }

    return {
      isLogin,
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
}

.auth-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-bottom: 15px;
  padding: 10px;
  background: #fee;
  border-radius: 5px;
  text-align: center;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.3s;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.switch-mode {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.switch-mode a {
  color: #667eea;
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
}

.switch-mode a:hover {
  text-decoration: underline;
}
</style>
