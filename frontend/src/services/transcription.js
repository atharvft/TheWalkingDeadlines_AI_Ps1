export async function transcribeAudio(audioBlob) {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'recording.webm')

  const response = await fetch('/api/transcription', {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    throw new Error('Transcription failed')
  }

  return response.json()
}

export function createAudioRecorder(onDataAvailable) {
  let mediaRecorder
  let chunks = []

  return {
    async start() {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      chunks = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data)
      }

      mediaRecorder.start(100)
      return stream
    },

    stop() {
      return new Promise((resolve) => {
        mediaRecorder.onstop = () => {
          const blob = new Blob(chunks, { type: 'audio/webm' })
          resolve(blob)
          mediaRecorder.stream.getTracks().forEach((track) => track.stop())
        }
        mediaRecorder.stop()
      })
    }
  }
}