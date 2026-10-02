import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppShell } from './components/ui'
import Overview from './pages/Overview'
import AIDesk from './pages/AIDesk'
import Operations from './pages/Operations'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <BrowserRouter>
      <AppShell><Routes>
        <Route path="/" element={<Overview />} />
        <Route path="/ai-desk" element={<AIDesk />} />
        <Route path="/orders" element={<Operations page="orders" />} />
        <Route path="/clarifications" element={<Operations page="clarifications" />} />
        <Route path="/products" element={<Operations page="products" />} />
        <Route path="/inventory" element={<Operations page="inventory" />} />
        <Route path="/customers" element={<Operations page="customers" />} />
        <Route path="/deliveries" element={<Operations page="deliveries" />} />
        <Route path="/billing" element={<Operations page="billing" />} />
        <Route path="/analytics" element={<Operations page="analytics" />} />
        <Route path="/settings" element={<Operations page="settings" />} />
        <Route path="/not-found" element={<NotFound />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes></AppShell>
    </BrowserRouter>
  )
}
