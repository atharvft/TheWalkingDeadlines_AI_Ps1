import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    const body = error.response?.data
    const proxyFailure = error.response?.status === 500 &&
      typeof body === 'string' &&
      /ECONNREFUSED|proxy error|socket hang up|connect error/i.test(body)

    if (proxyFailure || (!error.response && /network error/i.test(error.message || ''))) {
      error.message = 'The Order Desk backend is not running. Start the backend on port 8000, then try again.'
    } else if (error.response?.status === 500) {
      error.message = 'The server could not complete this request. Restart the backend and try again.'
    }
    return Promise.reject(error)
  }
)

export default api
