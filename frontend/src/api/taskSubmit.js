import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export const getTaskList = async () => {
  const response = await api.get('/task-submit/list')
  return response.data
}

export const createTask = async (taskData) => {
  const response = await api.post('/task-submit/create', taskData)
  return response.data
}

