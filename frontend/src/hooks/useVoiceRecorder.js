import { useState, useCallback, useRef } from 'react'
import { createAudioRecorder } from '../services/transcription'

export function useVoiceRecorder({ onTranscript, onError }) {
  const [isRecording, setIsRecording] = useState(false)
  const recorderRef = useRef(null)
  const streamRef = useRef(null)

  const startRecording = useCallback(async () => {
    try {
      recorderRef.current = createAudioRecorder()
      streamRef.current = await recorderRef.current.start()
      setIsRecording(true)
    } catch (err) {
      console.error('Failed to start recording:', err)
      onError?.(err.message || 'Microphone access was denied. Allow microphone access and try again.')
    }
  }, [])

  const stopRecording = useCallback(async () => {
    if (!recorderRef.current) return
    try {
      const audioBlob = await recorderRef.current.stop()
      setIsRecording(false)
      if (onTranscript) {
        await onTranscript(audioBlob)
      }
    } catch (err) {
      console.error('Failed to stop recording:', err)
      setIsRecording(false)
      onError?.(err.message || 'No audio was captured. Please try again.')
    }
  }, [onTranscript, onError])

  return { isRecording, startRecording, stopRecording }
}
