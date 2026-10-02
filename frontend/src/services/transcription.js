import api from './api'

export async function transcribeAudio(audioBlob) {
  if (!audioBlob || audioBlob.size === 0) {
    throw new Error('No audio was recorded. Please speak for a moment and try again.')
  }
  const formData = new FormData()
  const extension = audioBlob.type.includes('mp4') ? 'mp4' : audioBlob.type.includes('ogg') ? 'ogg' : 'webm'
  formData.append('audio', audioBlob, `recording.${extension}`)

  const response = await api.post('/transcribe', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

export function createAudioRecorder(onDataAvailable) {
  let mediaRecorder
  let chunks = []
  let stream
  let mimeType = ''

  const supportedMimeType = () => [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/mp4',
    'audio/ogg;codecs=opus'
  ].find((candidate) => window.MediaRecorder?.isTypeSupported?.(candidate)) || ''

  return {
    async start() {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mimeType = supportedMimeType()
      mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream)
      chunks = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data)
      }

      // Do not rely solely on a short timeslice: Safari and some mobile
      // browsers emit their only chunk when requestData()/stop() is called.
      mediaRecorder.start()
      return stream
    },

    stop() {
      return new Promise((resolve, reject) => {
        if (!mediaRecorder || mediaRecorder.state === 'inactive') {
          reject(new Error('Recording is not active. Please start recording again.'))
          return
        }
        mediaRecorder.onstop = () => {
          const blob = new Blob(chunks, { type: mimeType || mediaRecorder.mimeType || 'audio/webm' })
          stream?.getTracks().forEach((track) => track.stop())
          if (blob.size === 0) {
            reject(new Error('No audio was captured. Check microphone permission and speak before stopping.'))
            return
          }
          resolve(blob)
        }
        mediaRecorder.onerror = () => reject(new Error('The microphone recording failed. Please try again.'))
        mediaRecorder.requestData()
        mediaRecorder.stop()
      })
    }
  }
}
