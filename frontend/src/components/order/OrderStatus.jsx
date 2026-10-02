export default function OrderStatus({ status }) {
  const statusConfig = {
    pending: { label: 'Pending', className: 'bg-yellow-100 text-yellow-800' },
    processing: { label: 'Processing', className: 'bg-blue-100 text-blue-800' },
    confirmed: { label: 'Confirmed', className: 'bg-green-100 text-green-800' },
    ambiguous: { label: 'Needs Clarification', className: 'bg-orange-100 text-orange-800' },
    rejected: { label: 'Rejected', className: 'bg-red-100 text-red-800' },
    completed: { label: 'Completed', className: 'bg-purple-100 text-purple-800' }
  }

  const config = statusConfig[status] || { label: status, className: 'bg-gray-100 text-gray-800' }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}