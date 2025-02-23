import axios from "axios";

const api = axios.create({
  baseURL:"https://4ce8-2a02-2149-8adf-6f00-d635-2576-893e-9c49.ngrok-free.app/api", // CHANGE
  headers: {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
  },
});

// Automatically attach token if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle unauthorized errors (401) by clearing storage and redirecting to login
api.interceptors.response.use(
  response => response, 
  error => {
    if (error.response?.status === 401) {
      console.warn("Unauthorized request - clearing session data.");

      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      localStorage.removeItem("profile");

      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;