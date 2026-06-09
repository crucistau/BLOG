// @author beishi
// @date 2026/6/9
// @description Axios API wrapper with JWT interceptors for blog backend
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('devlog-token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('devlog-token')
      if (window.location.pathname.startsWith('/admin')) {
        window.location.href = '/admin/login'
      }
    }
    return Promise.reject(error)
  }
)

// --- Public API ---

export function getPosts(params = {}) {
  return api.get('/posts', { params })
}

export function getPost(slug) {
  return api.get(`/posts/${slug}`)
}

export function searchPosts(params = {}) {
  return api.get('/posts/search', { params })
}

export function getTags() {
  return api.get('/tags')
}

export function getCategories() {
  return api.get('/categories')
}

// --- Auth API ---

export function adminLogin(credentials) {
  return api.post('/auth/login', credentials)
}

// --- Admin Posts API ---

export function adminGetPosts(params = {}) {
  return api.get('/admin/posts', { params })
}

export function adminGetPost(id) {
  return api.get(`/admin/posts/${id}`)
}

export function adminCreatePost(data) {
  return api.post('/admin/posts', data)
}

export function adminUpdatePost(id, data) {
  return api.put(`/admin/posts/${id}`, data)
}

export function adminDeletePost(id) {
  return api.delete(`/admin/posts/${id}`)
}

export function adminTogglePublish(id) {
  return api.patch(`/admin/posts/${id}/toggle-publish`)
}

// --- Admin Tags API ---

export function adminGetTags() {
  return api.get('/admin/tags')
}

export function adminCreateTag(data) {
  return api.post('/admin/tags', data)
}

export function adminUpdateTag(id, data) {
  return api.put(`/admin/tags/${id}`, data)
}

export function adminDeleteTag(id) {
  return api.delete(`/admin/tags/${id}`)
}

// --- Admin Categories API ---

export function adminGetCategories() {
  return api.get('/admin/categories')
}

export function adminCreateCategory(data) {
  return api.post('/admin/categories', data)
}

export function adminUpdateCategory(id, data) {
  return api.put(`/admin/categories/${id}`, data)
}

export function adminDeleteCategory(id) {
  return api.delete(`/admin/categories/${id}`)
}

// === Analytics ===

export function trackPageView(path) {
  return api.post('/analytics/track', { path })
}

export function adminGetAnalyticsOverview() {
  return api.get('/admin/analytics/overview')
}

export function adminGetAnalyticsTrend(days = 7) {
  return api.get('/admin/analytics/trend', { params: { days } })
}

export function adminGetAnalyticsRegion() {
  return api.get('/admin/analytics/region')
}

export function adminGetAnalyticsCities(province) {
  return api.get('/admin/analytics/cities', { params: { province } })
}

export function adminGetPopularPages(limit = 10) {
  return api.get('/admin/analytics/popular-pages', { params: { limit } })
}

export function adminGetDevices() {
  return api.get('/admin/analytics/devices')
}

export function adminGetReferers(limit = 10) {
  return api.get('/admin/analytics/referers', { params: { limit } })
}

export default api
