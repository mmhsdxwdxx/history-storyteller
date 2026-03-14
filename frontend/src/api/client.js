import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

export const contentAPI = {
  list: () => api.get('/contents'),
  get: (id) => api.get(`/contents/${id}`),
  create: (data) => api.post('/contents', data),
  process: (id, provider) => api.post(`/contents/${id}/process`, null, { params: { provider } })
}
