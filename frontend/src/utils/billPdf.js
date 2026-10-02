import { jsPDF } from 'jspdf'

const SHOP = { name: 'Shree Ganesh Kirana', address: 'Your neighbourhood grocery store', phone: '+91 98765 00000' }
const money = (value) => `Rs. ${Number(value || 0).toFixed(2)}`
const invoiceNumber = (order) => `INV-${String(order.id || '').slice(0, 8).toUpperCase()}`
const orderDate = (order) => new Date(order.confirmed_at || order.created_at || Date.now()).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
const itemAmount = (item) => item.line_total ?? Number(item.quantity || 0) * Number(item.unit_price || 0)
const safeText = (value) => String(value || '').replace(/[<>]/g, '')

function drawHeader(pdf, order, page) {
  pdf.setFillColor(34, 78, 73)
  pdf.rect(0, 0, 210, 34, 'F')
  pdf.setTextColor(255, 255, 255)
  pdf.setFont('helvetica', 'bold')
  pdf.setFontSize(18)
  pdf.text(SHOP.name, 14, 16)
  pdf.setFont('helvetica', 'normal')
  pdf.setFontSize(8.5)
  pdf.text(SHOP.address, 14, 23)
  pdf.text(SHOP.phone, 14, 28)
  pdf.setFont('helvetica', 'bold')
  pdf.setFontSize(16)
  pdf.text('TAX INVOICE', 196, 16, { align: 'right' })
  pdf.setFont('helvetica', 'normal')
  pdf.setFontSize(8.5)
  pdf.text(invoiceNumber(order), 196, 23, { align: 'right' })
  pdf.text(`Page ${page}`, 196, 28, { align: 'right' })
  pdf.setTextColor(30, 41, 59)
  if (page > 1) return 44

  pdf.setDrawColor(208, 216, 214)
  pdf.setFillColor(248, 250, 249)
  pdf.roundedRect(14, 42, 88, 35, 2, 2, 'FD')
  pdf.roundedRect(108, 42, 88, 35, 2, 2, 'FD')
  pdf.setFont('helvetica', 'bold')
  pdf.setFontSize(9)
  pdf.text('BILL TO', 18, 49)
  pdf.text('INVOICE DETAILS', 112, 49)
  pdf.setFont('helvetica', 'normal')
  pdf.text(safeText(order.customer_name || 'Walk-in customer'), 18, 57)
  if (order.customer_phone) pdf.text(safeText(order.customer_phone), 18, 63)
  pdf.text(pdf.splitTextToSize(safeText(order.customer_address || 'Counter sale'), 78).slice(0, 2), 18, 69)
  pdf.text(`Order ID: ${String(order.id || '').slice(0, 13)}`, 112, 57)
  pdf.text(`Date: ${orderDate(order)}`, 112, 64)
  pdf.text('Status: Confirmed', 112, 71)
  return 86
}

function drawTableHeader(pdf, y) {
  pdf.setFillColor(34, 78, 73)
  pdf.rect(14, y, 182, 8, 'F')
  pdf.setTextColor(255, 255, 255)
  pdf.setFont('helvetica', 'bold')
  pdf.setFontSize(9)
  pdf.text('#', 17, y + 5.2)
  pdf.text('Item description', 27, y + 5.2)
  pdf.text('Qty', 123, y + 5.2)
  pdf.text('Rate', 145, y + 5.2)
  pdf.text('Amount', 192, y + 5.2, { align: 'right' })
  pdf.setTextColor(30, 41, 59)
  pdf.setFont('helvetica', 'normal')
  return y + 13
}

/** Download a printable invoice form using confirmed, deterministic bill values only. */
export function downloadBillPdf(order, bill) {
  const pdf = new jsPDF({ unit: 'mm', format: 'a4' })
  const source = bill || order
  const items = source.items || order?.items || []
  let page = 1
  let y = drawTableHeader(pdf, drawHeader(pdf, order, page))

  items.forEach((item, index) => {
    const description = `${safeText(item.product_name)}${item.brand ? ` — ${safeText(item.brand)}` : ''}`
    const lines = pdf.splitTextToSize(description, 90)
    const height = Math.max(9, lines.length * 4.2 + 4)
    if (y + height > 242) {
      pdf.addPage()
      page += 1
      y = drawTableHeader(pdf, drawHeader(pdf, order, page))
    }
    pdf.setDrawColor(226, 232, 240)
    pdf.line(14, y + height, 196, y + height)
    pdf.setFontSize(9)
    pdf.text(String(index + 1), 17, y + 5.2)
    pdf.text(lines, 27, y + 5.2)
    pdf.text(`${item.quantity} ${safeText(item.unit)}`, 123, y + 5.2)
    pdf.text(money(item.unit_price), 145, y + 5.2)
    pdf.text(money(itemAmount(item)), 192, y + 5.2, { align: 'right' })
    y += height
  })

  if (y > 214) {
    pdf.addPage()
    page += 1
    y = drawHeader(pdf, order, page)
  }
  y += 8
  pdf.setFillColor(248, 250, 249)
  pdf.roundedRect(116, y, 80, 34, 2, 2, 'F')
  pdf.setFontSize(9)
  pdf.text('Subtotal', 120, y + 8)
  pdf.text(money(source.subtotal), 192, y + 8, { align: 'right' })
  pdf.text(`Tax (${Number(source.tax_rate ?? 0.18) * 100}%)`, 120, y + 15)
  pdf.text(money(source.tax), 192, y + 15, { align: 'right' })
  pdf.setDrawColor(34, 78, 73)
  pdf.line(120, y + 20, 192, y + 20)
  pdf.setFont('helvetica', 'bold')
  pdf.setFontSize(12)
  pdf.text('GRAND TOTAL', 120, y + 28)
  pdf.text(money(source.total ?? source.total_amount), 192, y + 28, { align: 'right' })
  pdf.setFont('helvetica', 'normal')
  pdf.setFontSize(8)
  pdf.text('This is a computer-generated invoice. Thank you for shopping with us.', 14, 278)
  pdf.text('Customer signature: ____________________', 136, 278)
  pdf.save(`${invoiceNumber(order)}.pdf`)
}

/** Open the same invoice details in a browser-friendly printable form. */
export function printBill(order, bill) {
  const source = bill || order
  const items = source.items || order?.items || []
  const rows = items.map((item, index) => `<tr><td>${index + 1}</td><td><b>${safeText(item.product_name)}</b>${item.brand ? `<small>${safeText(item.brand)}</small>` : ''}</td><td>${safeText(item.quantity)} ${safeText(item.unit)}</td><td>${money(item.unit_price)}</td><td>${money(itemAmount(item))}</td></tr>`).join('')
  const popup = window.open('', '_blank', 'noopener,noreferrer')
  if (!popup) return
  popup.document.write(`<!doctype html><html><head><title>${invoiceNumber(order)}</title><style>body{font:13px Arial;color:#1e293b;margin:0;padding:28px}.header{background:#224e49;color:#fff;padding:22px;display:flex;justify-content:space-between}.header h1{font-size:22px;margin:0}.header p{margin:6px 0 0;font-size:11px}.details{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:18px 0}.box{border:1px solid #d8e0de;padding:12px;min-height:66px}.label{font-size:10px;font-weight:bold;color:#52616b;margin-bottom:8px}table{width:100%;border-collapse:collapse}th{background:#224e49;color:#fff;text-align:left;padding:9px;font-size:11px}td{border-bottom:1px solid #e2e8f0;padding:10px;vertical-align:top}td small{display:block;color:#64748b;margin-top:3px}.totals{width:300px;margin:20px 0 0 auto;background:#f8faf9;padding:14px}.totals div{display:flex;justify-content:space-between;margin:7px 0}.grand{border-top:1px solid #224e49;padding-top:8px;font-size:17px;font-weight:bold}@media print{body{padding:0}.header{-webkit-print-color-adjust:exact;print-color-adjust:exact}}</style></head><body><section class="header"><div><h1>${SHOP.name}</h1><p>${SHOP.address} · ${SHOP.phone}</p></div><div><b>TAX INVOICE</b><p>${invoiceNumber(order)}<br>${orderDate(order)}</p></div></section><section class="details"><div class="box"><div class="label">BILL TO</div><b>${safeText(order.customer_name || 'Walk-in customer')}</b><br>${safeText(order.customer_phone || '')}<br>${safeText(order.customer_address || 'Counter sale')}</div><div class="box"><div class="label">ORDER DETAILS</div>Order ID: ${safeText(order.id)}<br>Status: Confirmed<br>Payment: Pay at shop</div></section><table><thead><tr><th>#</th><th>Item description</th><th>Qty</th><th>Rate</th><th>Amount</th></tr></thead><tbody>${rows}</tbody></table><section class="totals"><div><span>Subtotal</span><span>${money(source.subtotal)}</span></div><div><span>Tax (${Number(source.tax_rate ?? 0.18) * 100}%)</span><span>${money(source.tax)}</span></div><div class="grand"><span>Grand total</span><span>${money(source.total ?? source.total_amount)}</span></div></section><p style="margin-top:42px;font-size:11px">This is a computer-generated invoice. Thank you for shopping with us.</p><script>window.onload=()=>window.print()<\/script></body></html>`)
  popup.document.close()
}
