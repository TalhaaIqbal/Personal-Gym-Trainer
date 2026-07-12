import axios from 'axios'

const API_URL =  process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refreshToken')
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken
        })

        const { access_token, refresh_token } = response.data
        localStorage.setItem('token', access_token)
        localStorage.setItem('refreshToken', refresh_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return axiosInstance(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')

        if (window.location.pathname !== '/') {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default axiosInstance