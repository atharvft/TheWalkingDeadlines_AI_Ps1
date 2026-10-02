export function formatCurrency(amount, currency = '₹') {
  return `${currency}${Number(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}