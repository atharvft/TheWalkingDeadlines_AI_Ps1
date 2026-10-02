export const ORDER_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  CONFIRMED: 'confirmed',
  AMBIGUOUS: 'ambiguous',
  REJECTED: 'rejected',
  COMPLETED: 'completed'
}

export const STATUS_LABELS = {
  [ORDER_STATUS.PENDING]: 'Pending',
  [ORDER_STATUS.PROCESSING]: 'Processing',
  [ORDER_STATUS.CONFIRMED]: 'Confirmed',
  [ORDER_STATUS.AMBIGUOUS]: 'Needs Clarification',
  [ORDER_STATUS.REJECTED]: 'Rejected',
  [ORDER_STATUS.COMPLETED]: 'Completed'
}

export const STATUS_COLORS = {
  [ORDER_STATUS.PENDING]: 'bg-yellow-100 text-yellow-800',
  [ORDER_STATUS.PROCESSING]: 'bg-blue-100 text-blue-800',
  [ORDER_STATUS.CONFIRMED]: 'bg-green-100 text-green-800',
  [ORDER_STATUS.AMBIGUOUS]: 'bg-orange-100 text-orange-800',
  [ORDER_STATUS.REJECTED]: 'bg-red-100 text-red-800',
  [ORDER_STATUS.COMPLETED]: 'bg-purple-100 text-purple-800'
}