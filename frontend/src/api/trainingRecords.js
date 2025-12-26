import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export const getTrainingRecords = async () => {
  const response = await api.get('/training/records')
  return response.data
}

export const createTrainingRecord = async (recordData) => {
  const response = await api.post('/training/records', recordData)
  return response.data
}

export const updateTrainingRecord = async (recordId, updateData) => {
  const response = await api.put(`/training/records/${recordId}`, updateData)
  return response.data
}

export const deleteTrainingRecord = async (recordId) => {
  const response = await api.delete(`/training/records/${recordId}`)
  return response.data
}
