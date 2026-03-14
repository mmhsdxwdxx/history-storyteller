import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000'
})

export const contentAPI = {
  list: () => api.get('/api/contents'),
  get: (id) => api.get(`/api/contents/${id}`),
  create: (data) => api.post('/api/contents', data),
  process: (id, provider) => api.post(`/api/contents/${id}/process`, null, { params: { provider } })
}
