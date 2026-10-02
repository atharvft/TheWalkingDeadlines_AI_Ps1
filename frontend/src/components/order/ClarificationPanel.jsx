export default function ClarificationPanel({ questions, onAnswer, onSkip }) {
  if (!questions?.length) return null

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
      <h3 className="font-semibold text-amber-900 mb-3">Clarification Needed</h3>
      <div className="space-y-3">
        {questions.map((q, index) => (
          <div key={index} className="bg-white p-3 rounded border">
            <p className="text-amber-800 mb-2">{q.question}</p>
            {q.options?.length ? (
              <div className="flex flex-wrap gap-2">
                {q.options.map((opt, i) => (
                  <button
                    key={i}
                    onClick={() => onAnswer?.(index, opt)}
                    className="px-3 py-1 bg-amber-100 text-amber-800 rounded hover:bg-amber-200 text-sm"
                  >
                    {opt}
                  </button>
                ))}
              </div>
            ) : (
              <input
                type="text"
                placeholder="Type your answer..."
                onKeyDown={(e) => e.key === 'Enter' && onAnswer?.(index, e.target.value)}
                className="w-full p-2 border border-amber-300 rounded focus:outline-none focus:ring-2 focus:ring-amber-500"
              />
            )}
            {q.suggestions?.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {q.suggestions.map((suggestion, i) => (
                  <button
                    key={i}
                    onClick={() => onAnswer?.(index, suggestion.product_name)}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded hover:bg-blue-200 text-sm"
                  >
                    Use {suggestion.product_name}
                  </button>
                ))}
              </div>
            )}
            {onSkip && (
              <button
                onClick={() => onSkip(index)}
                className="text-sm text-amber-600 hover:underline mt-1"
              >
                Skip
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
