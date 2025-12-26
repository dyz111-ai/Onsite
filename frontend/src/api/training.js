import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000 // 5分钟超时，因为训练可能需要时间
})

export const startTraining = async () => {
  const response = await api.post('/training/start')
  return response.data
}

export const getTrainingResult = async () => {
  const response = await api.get('/training/result')
  return response.data
}
