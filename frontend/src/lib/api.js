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

export const uploadApi = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data);
  },
};

export const ratingApi = {
  status: () => api.get('/rating/status').then(r => r.data),
  leaderboard: () => api.get('/rating/leaderboard').then(r => r.data),
};

export const referralApi = {
  apply: (code) => api.post('/referral/apply', { code }).then(r => r.data),
  stats: () => api.get('/referral/stats').then(r => r.data),
};

export const adminApi = {
  reviews: (status) => api.get('/admin/reviews', { params: status ? { status } : {} }).then(r => r.data),
  approveReview: (id) => api.put(`/admin/reviews/${id}/approve`).then(r => r.data),
  rejectReview: (id, reason) => api.put(`/admin/reviews/${id}/reject`, { reason }).then(r => r.data),
  stats: () => api.get('/admin/stats').then(r => r.data),
  users: () => api.get('/admin/users').then(r => r.data),
  setRole: (userId, role) => api.put(`/admin/users/${userId}/role`, { role }).then(r => r.data),
};

export const verificationApi = {
  status: () => api.get('/verification/status').then(r => r.data),
  sendPhoneCode: (phone) => api.post('/verification/phone', { phone }).then(r => r.data),
  confirmPhone: (code) => api.post('/verification/phone/confirm', { code }).then(r => r.data),
  verifyPassport: (data) => api.post('/verification/passport', data).then(r => r.data),
  verifyBankId: (bank) => api.post('/verification/bank-id', { bank }).then(r => r.data),
  verifyYandexId: () => api.post('/verification/yandex-id').then(r => r.data),
};

export const newsApi = {
  list: (params) => api.get('/news', { params }).then(r => r.data),
  get: (id) => api.get(`/news/${id}`).then(r => r.data),
  create: (data) => api.post('/news', data).then(r => r.data),
  like: (id) => api.post(`/news/${id}/like`).then(r => r.data),
  comments: (id) => api.get(`/news/${id}/comments`).then(r => r.data),
  addComment: (id, text) => api.post(`/news/${id}/comments`, { text }).then(r => r.data),
};

export const widgetsApi = {
  weather: (lat, lon) => api.get('/widgets/weather', { params: { lat, lon } }).then(r => r.data),
  currency: () => api.get('/widgets/currency').then(r => r.data),
  magnetic: () => api.get('/widgets/magnetic').then(r => r.data),
  searchLocations: (q) => api.get('/widgets/locations', { params: { q } }).then(r => r.data),
};

export const mapApi = {
  problems: () => api.get('/map/problems').then(r => r.data),
};

export const onboardingApi = {
  status: () => api.get('/onboarding/status').then(r => r.data),
  complete: (data) => api.post('/onboarding/complete', data).then(r => r.data),
};

export const missionsApi = {
  daily: () => api.get('/missions/daily').then(r => r.data),
  progress: (id, increment = 1) => api.post(`/missions/${id}/progress`, { increment }).then(r => r.data),
  claim: (id) => api.post(`/missions/${id}/claim`).then(r => r.data),
};

export const verifyFeedApi = {
  pending: () => api.get('/reviews/pending-verification').then(r => r.data),
};

export default api;
