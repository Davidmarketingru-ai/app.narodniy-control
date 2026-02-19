import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API,
  withCredentials: true,
});

export const reviewsApi = {
  list: (params) => api.get('/reviews', { params }).then(r => r.data),
  get: (id) => api.get(`/reviews/${id}`).then(r => r.data),
  create: (data) => api.post('/reviews', data).then(r => r.data),
};

export const organizationsApi = {
  list: () => api.get('/organizations').then(r => r.data),
  get: (id) => api.get(`/organizations/${id}`).then(r => r.data),
  create: (data) => api.post('/organizations', data).then(r => r.data),
};

export const verificationsApi = {
  create: (data) => api.post('/verifications', data).then(r => r.data),
  getByReview: (reviewId) => api.get(`/verifications/${reviewId}`).then(r => r.data),
};

export const notificationsApi = {
  list: () => api.get('/notifications').then(r => r.data),
  markRead: (id) => api.put(`/notifications/${id}/read`).then(r => r.data),
  markAllRead: () => api.put('/notifications/read-all').then(r => r.data),
};

export const pointsApi = {
  balance: () => api.get('/points/balance').then(r => r.data),
  history: () => api.get('/points/history').then(r => r.data),
};

export const rewardsApi = {
  list: (ageGroup) => api.get('/rewards', { params: ageGroup ? { age_group: ageGroup } : {} }).then(r => r.data),
  redeem: (rewardId) => api.post(`/rewards/${rewardId}/redeem`).then(r => r.data),
};

export const profileApi = {
  get: () => api.get('/profile').then(r => r.data),
  update: (data) => api.put('/profile', data).then(r => r.data),
};

export default api;
