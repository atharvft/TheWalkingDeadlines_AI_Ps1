export const dashboardOrders = [
  { id: 'ORD-1024', customer: 'Rahul Sharma', phone: '+91 98765 42110', source: 'WhatsApp', items: '4 items', amount: '₹375', delivery: 'Tomorrow · 9:00 AM', status: 'Pending clarification' },
  { id: 'ORD-1023', customer: 'Priya Mehta', phone: '+91 99887 21440', source: 'Physical shop', items: '6 items', amount: '₹820', delivery: 'Today · 6:30 PM', status: 'Confirmed' },
  { id: 'ORD-1022', customer: 'Amit Verma', phone: '+91 98100 71220', source: 'WhatsApp', items: '3 items', amount: '₹290', delivery: 'Today · 4:00 PM', status: 'Packing' },
  { id: 'ORD-1021', customer: 'Neha Kapoor', phone: '+91 99110 30214', source: 'WhatsApp', items: '8 items', amount: '₹1,240', delivery: 'Today · 2:30 PM', status: 'Out for delivery' },
  { id: 'ORD-1020', customer: 'Vikram Singh', phone: '+91 98711 45291', source: 'Physical shop', items: '2 items', amount: '₹180', delivery: 'Delivered', status: 'Delivered' }
]

export const products = [
  { name: 'Aashirvaad Whole Wheat Atta', brand: 'Aashirvaad', category: 'Staples', pack: '1kg', price: '₹62', stock: 24, threshold: 8, state: 'Healthy' },
  { name: 'Aashirvaad Whole Wheat Atta', brand: 'Aashirvaad', category: 'Staples', pack: '5kg', price: '₹285', stock: 9, threshold: 5, state: 'Healthy' },
  { name: 'Amul Salted Butter', brand: 'Amul', category: 'Dairy', pack: '100g', price: '₹60', stock: 2, threshold: 10, state: 'Low stock' },
  { name: 'Amul Salted Butter', brand: 'Amul', category: 'Dairy', pack: '500g', price: '₹285', stock: 11, threshold: 5, state: 'Healthy' },
  { name: 'Fortune Sunflower Oil', brand: 'Fortune', category: 'Staples', pack: '1L', price: '₹145', stock: 0, threshold: 6, state: 'Out of stock' },
  { name: 'Fortune Sunflower Oil', brand: 'Fortune', category: 'Staples', pack: '5L', price: '₹690', stock: 7, threshold: 3, state: 'Healthy' },
  { name: 'Sugar', brand: 'Generic', category: 'Staples', pack: '1kg', price: '₹48', stock: 32, threshold: 10, state: 'Healthy' },
  { name: 'Tata Salt', brand: 'Tata', category: 'Staples', pack: '1kg', price: '₹25', stock: 5, threshold: 8, state: 'Low stock' }
]

export const customers = [
  { name: 'Rahul Sharma', phone: '+91 98765 42110', orders: 18, spend: '₹12,480', last: 'Today, 10:42 AM', favourite: 'Atta · Oil' },
  { name: 'Priya Mehta', phone: '+91 99887 21440', orders: 12, spend: '₹8,920', last: 'Yesterday, 6:15 PM', favourite: 'Dairy · Snacks' },
  { name: 'Amit Verma', phone: '+91 98100 71220', orders: 9, spend: '₹5,640', last: 'Today, 1:04 PM', favourite: 'Staples' },
  { name: 'Neha Kapoor', phone: '+91 99110 30214', orders: 7, spend: '₹4,290', last: 'Mon, 8:30 AM', favourite: 'Fresh produce' }
]

export const clarificationCards = [
  { customer: 'Rahul Sharma', id: 'ORD-1024', phrase: '2 kilo atta aur tel bhi dena', issue: 'Oil type and pack size are missing.', candidates: ['Fortune Sunflower Oil 1L', 'Fortune Sunflower Oil 5L', 'Dhara Groundnut Oil 1L'], reply: 'Kaunsa oil chahiye – sunflower, groundnut ya mustard? Aur 1L ya 5L?' },
  { customer: 'Sana Khan', id: 'ORD-1018', phrase: 'Amul butter ek packet', issue: 'Pack size is not specified.', candidates: ['Amul Butter 100g', 'Amul Butter 500g'], reply: 'Amul butter 100g chahiye ya 500g?' }
]

export const deliveryColumns = {
  Confirmed: [{ id: 'ORD-1023', customer: 'Priya Mehta', time: '6:30 PM', amount: '₹820', items: '6 items' }],
  Packing: [{ id: 'ORD-1022', customer: 'Amit Verma', time: '4:00 PM', amount: '₹290', items: '3 items' }],
  Ready: [{ id: 'ORD-1019', customer: 'Karan Joshi', time: '3:45 PM', amount: '₹540', items: '5 items' }],
  'Out for delivery': [{ id: 'ORD-1021', customer: 'Neha Kapoor', time: '2:30 PM', amount: '₹1,240', items: '8 items' }],
  Delivered: [{ id: 'ORD-1020', customer: 'Vikram Singh', time: '12:15 PM', amount: '₹180', items: '2 items' }]
}

export const analysisPreview = [
  { name: 'Aashirvaad Atta', detail: '2 kg · Staples', confidence: 97, tag: 'Matched', tone: 'good' },
  { name: 'Amul Butter', detail: 'Quantity: 1 · Pack size missing', confidence: 86, tag: 'Needs confirmation', tone: 'warn' },
  { name: 'Sugar', detail: '500g · Generic', confidence: 98, tag: 'Matched', tone: 'good' },
  { name: 'Oil', detail: 'Type and pack size missing · 6 candidates', confidence: 42, tag: 'Clarification required', tone: 'ambiguous' }
]
