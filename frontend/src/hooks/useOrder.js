import { useState, useCallback } from 'react'
import {
  createOrder,
  submitVoiceOrder,
  answerClarification,
  skipClarification,
  confirmOrder
} from '../services/orderService'

export function useOrder() {
  const [order, setOrder] = useState(null)
  const [status, setStatus] = useState('pending')
  const [clarificationQuestions, setClarificationQuestions] = useState([])
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleError = (err) => {
    setError(err.response?.data?.detail || err.message || 'An error occurred')
    setIsLoading(false)
  }

  const submitTextOrder = useCallback(async (text) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await createOrder(text)
      setOrder(result.order)
      setStatus(result.status)
      setClarificationQuestions(result.clarification_questions || [])
    } catch (err) {
      handleError(err)
    }
  }, [])

  const submitVoiceOrderFn = useCallback(async (audioBlob) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await submitVoiceOrder(audioBlob)
      setOrder(result.order)
      setStatus(result.status)
      setClarificationQuestions(result.clarification_questions || [])
    } catch (err) {
      handleError(err)
    }
  }, [])

  const answerClarificationFn = useCallback(async (questionIndex, answer) => {
    setIsLoading(true)
    try {
      const result = await answerClarification(order.id, questionIndex, answer)
      setOrder(result.order)
      setStatus(result.status)
      setClarificationQuestions(result.clarification_questions || [])
    } catch (err) {
      handleError(err)
    }
  }, [order?.id])

  const skipClarificationFn = useCallback(async (questionIndex) => {
    setIsLoading(true)
    try {
      const result = await skipClarification(order.id, questionIndex)
      setOrder(result.order)
      setStatus(result.status)
      setClarificationQuestions(result.clarification_questions || [])
    } catch (err) {
      handleError(err)
    }
  }, [order?.id])

  const confirmOrderFn = useCallback(async () => {
    setIsLoading(true)
    try {
      const result = await confirmOrder(order.id)
      setOrder(result.order)
      setStatus(result.status)
    } catch (err) {
      handleError(err)
    }
  }, [order?.id])

  const resetOrder = useCallback(() => {
    setOrder(null)
    setStatus('pending')
    setClarificationQuestions([])
    setError(null)
  }, [])

  return {
    order,
    status,
    clarificationQuestions,
    error,
    isLoading,
    submitTextOrder,
    submitVoiceOrder: submitVoiceOrderFn,
    answerClarification: answerClarificationFn,
    skipClarification: skipClarificationFn,
    confirmOrder: confirmOrderFn,
    resetOrder
  }
}