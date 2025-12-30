import api from './auth'

// 获取赛题列表
export const getCompetitions = async () => {
  const response = await api.get('/competition/list')
  return response.data
}

// 选择测试赛题
export const selectCompetition = async (data) => {
  const response = await api.post('/competition/select', data)
  return response.data
}
