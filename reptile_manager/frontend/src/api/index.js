import axios from 'axios'

/**
 * Resolve the API base URL.
 *
 * Priority:
 *  1. window.__REPTILE_API__  — set by run.sh from add-on options (api_url)
 *  2. import.meta.env.VITE_API_URL — set at Vite build time (docker-compose)
 *  3. Auto-detect from HA Ingress pathname
 */
export function buildBaseURL() {
  // 1. Runtime config written by run.sh
  if (window.__REPTILE_API__) return window.__REPTILE_API__

  // 2. Build-time env (docker-compose mode)
  const env = import.meta.env.VITE_API_URL
  if (env) return env

  // 3. HA Ingress auto-detect:
  //    Page is at https://ha:8123/api/hassio_ingress/TOKEN/
  //    We construct the full URL so axios does not strip the ingress path.
  const pathname = window.location.pathname.replace(/\/+$/, '')
  return window.location.origin + pathname + '/api'
}

const api = axios.create({
  baseURL: buildBaseURL(),
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  r => r,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = './'
    }
    return Promise.reject(error)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const auth = {
  login(username, password) {
    const form = new URLSearchParams({ username, password })
    return api.post('/auth/token', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },
  me: () => api.get('/auth/me')
}

export const dashboard  = { stats: () => api.get('/dashboard') }

export const animals = {
  list:        p      => api.get('/animals', { params: p }),
  get:         id     => api.get(`/animals/${id}`),
  create:      data   => api.post('/animals', data),
  update:      (id,d) => api.put(`/animals/${id}`, d),
  delete:      id     => api.delete(`/animals/${id}`),
  feedings:    (id,p) => api.get(`/animals/${id}/feedings`, { params: p }),
  sheddings:   (id,p) => api.get(`/animals/${id}/sheddings`, { params: p }),
  weights:     (id,p) => api.get(`/animals/${id}/weights`, { params: p }),
  lengths:     (id,p) => api.get(`/animals/${id}/lengths`, { params: p }),
  tree:        id     => api.get(`/animals/${id}/tree`),
  uploadPhoto: (id, file) => {
    const form = new FormData(); form.append('file', file)
    return api.post(`/animals/${id}/photo`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  deletePhoto: id => api.delete(`/animals/${id}/photo`),
}

export const feedings   = { list: p => api.get('/feedings', { params: p }), create: d => api.post('/feedings', d), update: (id,d) => api.put(`/feedings/${id}`,d), delete: id => api.delete(`/feedings/${id}`) }
export const sheddings  = { list: p => api.get('/sheddings',{ params: p }), create: d => api.post('/sheddings',d), update: (id,d) => api.put(`/sheddings/${id}`,d), delete: id => api.delete(`/sheddings/${id}`) }
export const weights    = { list: p => api.get('/weights',  { params: p }), create: d => api.post('/weights', d),  update: (id,d) => api.put(`/weights/${id}`,d),  delete: id => api.delete(`/weights/${id}`) }
export const lengths    = { list: p => api.get('/lengths',  { params: p }), create: d => api.post('/lengths', d),  update: (id,d) => api.put(`/lengths/${id}`,d),  delete: id => api.delete(`/lengths/${id}`) }
export const breeding   = { list: p => api.get('/breeding', { params: p }), create: d => api.post('/breeding', d), update: (id,d) => api.put(`/breeding/${id}`,d), delete: id => api.delete(`/breeding/${id}`) }
export const customFields = { list: aid => api.get(`/custom-fields/animal/${aid}`), create: (aid,d) => api.post(`/custom-fields/animal/${aid}`,d), update: (fid,d) => api.put(`/custom-fields/${fid}`,d), delete: fid => api.delete(`/custom-fields/${fid}`) }
export const ha = { getConfig: () => api.get('/ha/config'), updateConfig: d => api.put('/ha/config',d), test: () => api.post('/ha/test'), sync: () => api.post('/ha/sync') }

export default api

// ── Bulk create ───────────────────────────────────────────────────────────────
export const bulk = {
  createAnimals: (quantity, animalData) =>
    api.post('/animals/bulk', { quantity, animal_data: animalData })
}

// ── Export ────────────────────────────────────────────────────────────────────
export const exportApi = {
  inventory: () =>
    api.get('/export/inventory', { responseType: 'blob' }),
  herkunftsnachweis: (data) =>
    api.post('/export/herkunftsnachweis', data, { responseType: 'blob' }),
}
