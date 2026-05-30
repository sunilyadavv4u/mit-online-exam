import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || '';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

const ACCESS_TOKEN_KEY = 'mit_access';
const REFRESH_TOKEN_KEY = 'mit_refresh';

export const tokenStore = {
  getAccess: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  set: ({ access, refresh } = {}) => {
    if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

apiClient.interceptors.request.use((config) => {
  const token = tokenStore.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise = null;
const refreshAccessToken = async () => {
  if (!refreshPromise) {
    const refresh = tokenStore.getRefresh();
    if (!refresh) return null;
    refreshPromise = axios
      .post(`${API_BASE_URL}/api/v1/auth/refresh/`, { refresh })
      .then((r) => {
        tokenStore.set({ access: r.data.access, refresh: r.data.refresh || refresh });
        return r.data.access;
      })
      .catch(() => {
        tokenStore.clear();
        return null;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
};

apiClient.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config;
    if (
      error.response?.status === 401 &&
      !original._retry &&
      !original.url.includes('/auth/login') &&
      !original.url.includes('/auth/refresh')
    ) {
      original._retry = true;
      const newAccess = await refreshAccessToken();
      if (newAccess) {
        original.headers.Authorization = `Bearer ${newAccess}`;
        return apiClient(original);
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
export { API_BASE_URL };
