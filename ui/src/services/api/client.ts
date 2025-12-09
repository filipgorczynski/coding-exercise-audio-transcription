import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  // 15 minutes (as we have long processing times)
  // TODO(fgorczynski): "fix" by providing approach like Celery
  timeout: 900000,
  headers: {
    "Content-Type": "application/json",
  },
});

// REQUEST interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => Promise.reject(error),
);

// RESPONSE interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || "An error occurred";
    return Promise.reject({ message, status: error.response?.status });
  },
);
