export default function DeliveryNote({ order, shopInfo }) {
  if (!order) return null

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 max-w-md mx-auto">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold">{shopInfo?.name || 'Shop Name'}</h2>
        <p className="text-gray-600">{shopInfo?.address || 'Shop Address'}</p>
        <p className="text-gray-600">{shopInfo?.phone || 'Contact'}</p>
      </div>
      <div className="border-t border-b py-4 mb-4">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div><span className="font-medium">Order ID:</span> {order.id}</div>
          <div><span className="font-medium">Date:</span> {new Date(order.created_at).toLocaleDateString()}</div>
          <div><span className="font-medium">Customer:</span> {order.customer_name}</div>
          <div><span className="font-medium">Phone:</span> {order.customer_phone}</div>
        </div>
      </div>
      <div className="space-y-2 mb-4">
        {order.items?.map((item, index) => (
          <div key={index} className="flex justify-between text-sm border-b pb-2">
            <span>{item.product_name} × {item.quantity} {item.unit}</span>
            <span>{item.unit_price * item.quantity}</span>
          </div>
        ))}
      </div>
      <div className="text-right font-bold text-lg">
        Total: ₹{order.total_amount?.toFixed(2) || '0.00'}
      </div>
    </div>
  )
}