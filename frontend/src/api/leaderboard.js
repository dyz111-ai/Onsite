import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
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

/**
 * 获取排行榜数据
 * @returns {Promise} - 排行榜数据
 */
export const getLeaderboardData = async () => {
  const response = await api.get('/leaderboard/list')
  return response.data
}

/**
 * 获取当前用户的最佳成绩
 * @returns {Promise} - 用户最佳成绩
 */
export const getUserBestScore = async () => {
  const response = await api.get('/leaderboard/user/best')
  return response.data
}

/**
 * 获取赛题列表（用于筛选）
 * @returns {Promise} - 赛题列表
 */
export const getCompetitionList = async () => {
  const response = await api.get('/competition/list')
  return response.data
}

export default api