/**
 * API client for the Timeline AI backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Image API endpoints
 */
export const imagesAPI = {
  list: (params = {}) => apiClient.get('/images', { params }),
  get: (id) => apiClient.get(`/images/${id}`),
  getThumbnail: (id, size = 300) => `${API_BASE_URL}/api/images/${id}/thumbnail?size=${size}`,
  getOriginal: (id) => `${API_BASE_URL}/api/images/${id}/original`,
  getStats: () => apiClient.get('/stats'),
};

/**
 * Timeline API endpoints
 */
export const timelineAPI = {
  getTimeline: (params = {}) => apiClient.get('/timeline', { params }),
  getTags: (tagType = null) =>
    apiClient.get('/tags', { params: tagType ? { tag_type: tagType } : {} }),
  getLocations: () => apiClient.get('/locations'),
};

/**
 * Processing API endpoints
 */
export const processingAPI = {
  scan: (folderPath, recursive = true) =>
    apiClient.post('/scan', { folder_path: folderPath, recursive }),
  extractExif: () => apiClient.post('/extract-exif'),
  analyze: (imageIds = null, force = false) =>
    apiClient.post('/analyze', { image_ids: imageIds, force }),
  processAll: (folderPath = null) =>
    apiClient.post('/process-all', null, { params: { folder_path: folderPath } }),
};

export default apiClient;
