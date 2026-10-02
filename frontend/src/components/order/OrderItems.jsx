export default function OrderItems({ items, onUpdateQuantity, onRemove, readOnly }) {
  if (!items?.length) {
    return <p className="text-gray-500 text-center py-4">No items in order</p>
  }

  return (
    <div className="space-y-2">
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
          <div className="flex-1 min-w-0">
            <p className="font-medium truncate">{item.product_name || item.name}</p>
            <p className="text-sm text-gray-500">
              {item.brand && `${item.brand} • `}
              {item.quantity} {item.unit}
            </p>
          </div>
          {!readOnly && (
            <div className="flex items-center gap-2">
              <input
                type="number"
                value={item.quantity}
                onChange={(e) => onUpdateQuantity?.(index, Number(e.target.value))}
                min="1"
                className="w-16 p-1 border border-gray-300 rounded text-center"
              />
              <button
                onClick={() => onRemove?.(index)}
                className="text-red-500 hover:text-red-700 p-1"
                aria-label="Remove item"
              >
                🗑️
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}