import api from './api'

export async function createOrder(text) {
  const response = await api.post('/orders', { text })
  return response.data
}

export async function submitVoiceOrder(audioBlob) {
  const formData = new FormData()
  formData.append('audio', audioBlob)
  const response = await api.post('/orders/voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

export async function getOrder(orderId) {
  const response = await api.get(`/orders/${orderId}`)
  return response.data
}

export async function answerClarification(orderId, questionIndex, answer) {
  const response = await api.post(`/orders/${orderId}/clarify`, {
    question_index: questionIndex,
    answer
  })
  return response.data
}

export async function skipClarification(orderId, questionIndex) {
  const response = await api.post(`/orders/${orderId}/clarify/skip`, {
    question_index: questionIndex
  })
  return response.data
}

export async function confirmOrder(orderId) {
  const response = await api.post(`/orders/${orderId}/confirm`)
  return response.data
}

export async function getBill(orderId) {
  const response = await api.get(`/orders/${orderId}/bill`)
  return response.data
}

export async function getDeliveryNote(orderId) {
  const response = await api.get(`/orders/${orderId}/delivery-note`)
  return response.data
}