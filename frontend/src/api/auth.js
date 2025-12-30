import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加 token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理 token 过期
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // token 过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 注册
export const register = async (data) => {
  const response = await api.post('/auth/register', data)
  return response.data
}

// 登录
export const login = async (data) => {
  const response = await api.post('/auth/login', data)
  return response.data
}

// 获取当前用户信息
export const getCurrentUser = async () => {
  const response = await api.get('/auth/me')
  return response.data
}

// 修改密码
export const changePassword = async (data) => {
  const response = await api.post('/auth/change-password', data)
  return response.data
}

// 管理员登录
export const adminLogin = async (data) => {
  const response = await api.post('/auth/admin/login', data)
  return response.data
}

export default api
