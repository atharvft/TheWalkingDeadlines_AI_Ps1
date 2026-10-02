export default function VoiceRecorder({ onStart, onStop, isRecording, disabled }) {
  return (
    <button
      onClick={isRecording ? onStop : onStart}
      disabled={disabled}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
        isRecording
          ? 'bg-red-100 text-red-700 hover:bg-red-200'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      aria-label={isRecording ? 'Stop recording' : 'Start recording'}
    >
      <span className={`w-2 h-2 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-400'}`} />
      <span>{isRecording ? 'Recording...' : 'Record'}</span>
    </button>
  )
}