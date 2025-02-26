import axios from "axios";
import { useAuthStore } from "../stores/auth";

const api = axios.create({
  baseURL: "https://b824-2a02-2149-8adf-6f00-9090-8539-7394-77e5.ngrok-free.app/api", // CHANGE
  headers: {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
  },
});

// Request interceptor: attach access token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: if a 401 is received, try refreshing the token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const store = useAuthStore();
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        try {
          // Call the refresh endpoint, save new tokens and update auth store / headers
          const { data } = await axios.post("https://154a-2a02-2149-8adf-6f00-9090-8539-7394-77e5.ngrok-free.app/api/token/refresh/", {
            refresh,
          });
          localStorage.setItem("access_token", data.access);
          localStorage.setItem("refresh_token", data.refresh);
          store.login(data.access, data.refresh, store.user!);
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          return api(originalRequest);
        } catch (err) {
          store.logout();
          return Promise.reject(err);
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;