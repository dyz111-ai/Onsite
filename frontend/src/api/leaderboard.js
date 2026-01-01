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
 * 获取总分排行榜数据
 * @returns {Promise} - 总分排行榜数据
 */
export const getLeaderboardData = async () => {
  const response = await api.get('/leaderboard/list')
  return response.data
}

/**
 * 获取成本排行榜数据
 * @returns {Promise} - 成本排行榜数据
 */
export const getCostLeaderboardData = async () => {
  const response = await api.get('/leaderboard/cost')
  return response.data
}

/**
 * 获取测试分数排行榜数据
 * @returns {Promise} - 测试分数排行榜数据
 */
export const getTestScoreLeaderboardData = async () => {
  const response = await api.get('/leaderboard/test_score')
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

/**
 * 获取当前用户在总分排行榜中的排名
 * @returns {Promise} - 用户总分排名
 */
export const getUserRankTotal = async () => {
  const response = await api.get('/leaderboard/user/rank/total')
  return response.data
}

/**
 * 获取当前用户在训练成本排行榜中的排名
 * @returns {Promise} - 用户成本排名
 */
export const getUserRankCost = async () => {
  const response = await api.get('/leaderboard/user/rank/cost')
  return response.data
}

/**
 * 获取当前用户在测试分数排行榜中的排名
 * @returns {Promise} - 用户测试分数排名
 */
export const getUserRankTest = async () => {
  const response = await api.get('/leaderboard/user/rank/test')
  return response.data
}

export default api