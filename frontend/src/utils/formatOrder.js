export function formatOrderForDisplay(order) {
  if (!order) return null
  return {
    ...order,
    items: order.items?.map(item => ({
      ...item,
      display_name: `${item.product_name} (${item.brand || 'Generic'})`,
      display_quantity: `${item.quantity} ${item.unit}`,
      line_total: item.unit_price * item.quantity
    }))
  }
}

export function calculateOrderTotals(items) {
  const subtotal = items.reduce((sum, item) => sum + item.unit_price * item.quantity, 0)
  const tax = subtotal * 0.18
  return { subtotal, tax, total: subtotal + tax }
}