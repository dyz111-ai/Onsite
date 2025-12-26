import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export const getCompetitionList = async () => {
  const response = await api.get('/competition/list')
  return response.data
}

