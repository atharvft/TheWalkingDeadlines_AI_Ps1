export default function BillSummary({ order, currency = '₹' }) {
  if (!order?.items?.length) return null

  const previewSubtotal = order.items.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0)
  const subtotal = order.status === 'confirmed' ? Number(order.subtotal) : previewSubtotal
  const tax = order.status === 'confirmed' ? Number(order.tax) : 0
  const total = order.status === 'confirmed' ? Number(order.total_amount) : subtotal

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <h3 className="font-semibold mb-4">Bill Summary</h3>
      <div className="space-y-2">
        {order.items.map((item, index) => (
          <div key={index} className="flex justify-between text-sm">
            <span>{item.product_name} × {item.quantity}</span>
            <span>{currency}{item.unit_price * item.quantity}</span>
          </div>
        ))}
        <div className="border-t pt-2 space-y-1">
          <div className="flex justify-between">
            <span>Subtotal</span>
            <span>{currency}{subtotal.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span>{order.status === 'confirmed' ? 'Tax (18%)' : 'Tax calculated at confirmation'}</span>
            <span>{currency}{tax.toFixed(2)}</span>
          </div>
          <div className="flex justify-between font-semibold text-lg border-t pt-2">
            <span>Total</span>
            <span>{currency}{total.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
