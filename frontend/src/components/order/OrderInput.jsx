export default function OrderInput({ value, onChange, onSubmit, placeholder, disabled }) {
  return (
    <div className="flex gap-2">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && onSubmit?.()}
        placeholder={placeholder}
        disabled={disabled}
        className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none min-h-[80px]"
        rows={3}
      />
      <button
        onClick={onSubmit}
        disabled={disabled || !value?.trim()}
        className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </div>
  )
}