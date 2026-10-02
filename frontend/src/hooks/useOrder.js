import { useState, useCallback } from 'react'
import {
  createOrder,
  answerClarification,
  skipClarification,
  confirmOrder,
  getBill
} from '../services/orderService'
import { transcribeAudio } from '../services/transcription'

export function useOrder() {
  const [order, setOrder] = useState(null)
  const [status, setStatus] = useState('pending')
  const [clarificationQuestions, setClarificationQuestions] = useState([])
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [voiceState, setVoiceState] = useState('IDLE')
  const [transcript, setTranscript] = useState('')
  const [bill, setBill] = useState(null)

  const handleError = (err) => {
    const detail = err.response?.data?.detail
    setError(detail?.message || (typeof detail === 'string' ? detail : null) || err.message || 'An error occurred')
    setIsLoading(false)
    setVoiceState('ERROR')
  }

  const submitTextOrder = useCallback(async (text, customer) => {
    setIsLoading(true)
    setError(null)
    setVoiceState('PROCESSING_ORDER')
    try {
      const result = await createOrder(text, customer)
      setOrder(result.order)
      setStatus(result.status)
      setClarificationQuestions(result.clarification_questions || [])
      setVoiceState('SUCCESS')
    } catch (err) {
      handleError(err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const submitVoiceOrderFn = useCallback(async (audioBlob, customer) => {
    setIsLoading(true)
    setError(null)
    setVoiceState('UPLOADING')
    try {
      setVoiceState('TRANSCRIBING')
      const transcription = await transcribeAudio(audioBlob)
      setTranscript(transcription.transcript || '')
      setVoiceState('PROCESSING_ORDER')
      const result = await createOrder(transcription.transcript, customer)
      setOrder(result.order)
      setStatus(result.status)
      setClarificationQuestions(result.clarification_questions || [])
      setVoiceState('SUCCESS')
    } catch (err) {
      handleError(err)
    } finally {
      setIsLoading(false)
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
    } finally {
      setIsLoading(false)
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
    } finally {
      setIsLoading(false)
    }
  }, [order?.id])

  const confirmOrderFn = useCallback(async () => {
    setIsLoading(true)
    try {
      const result = await confirmOrder(order.id)
      setOrder(result.order)
      setStatus(result.status)
      setBill(await getBill(order.id))
    } catch (err) {
      handleError(err)
    } finally {
      setIsLoading(false)
    }
  }, [order?.id])

  const resetOrder = useCallback(() => {
    setOrder(null)
    setStatus('pending')
    setClarificationQuestions([])
    setError(null)
    setVoiceState('IDLE')
    setTranscript('')
    setBill(null)
  }, [])

  const reportVoiceError = useCallback((message) => {
    setError(message || 'Voice processing failed. Please try again.')
    setVoiceState('ERROR')
    setIsLoading(false)
  }, [])

  return {
    order,
    status,
    clarificationQuestions,
    error,
    isLoading,
    voiceState,
    transcript,
    bill,
    submitTextOrder,
    submitVoiceOrder: submitVoiceOrderFn,
    answerClarification: answerClarificationFn,
    skipClarification: skipClarificationFn,
    confirmOrder: confirmOrderFn,
    reportVoiceError,
    resetOrder
  }
}
