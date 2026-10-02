import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import OrderDesk from './pages/OrderDesk'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<OrderDesk />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}