export default function ErrorMessage({ message, onDismiss }) {
  if (!message) return null
  return (
    <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded flex items-center justify-between">
      <span>{message}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="text-red-600 hover:text-red-800 font-bold text-lg leading-none px-2">
          ×
        </button>
      )}
    </div>
  )
}