import { useState } from 'react'
import { Icon, Button, PageHeader, StatusBadge } from '../components/ui'
import { useOrder } from '../hooks/useOrder'
import { useVoiceRecorder } from '../hooks/useVoiceRecorder'
import { downloadBillPdf, printBill } from '../utils/billPdf'

const voiceMessages = {
  IDLE: 'Ready to record Hindi, English, or Hinglish.',
  UPLOADING: 'Uploading audio…',
  TRANSCRIBING: 'Transcribing your order…',
  PROCESSING_ORDER: 'Understanding order and checking products…',
  SUCCESS: 'Order processed.',
  ERROR: 'Voice processing failed. Please try again.'
}

export default function AIDesk() {
  const [tab, setTab] = useState('Text order')
  const [text, setText] = useState('')
  const [customerName, setCustomerName] = useState('')
  const [customerPhone, setCustomerPhone] = useState('')
  const [customerAddress, setCustomerAddress] = useState('')
  const {
    order, bill, status, transcript, voiceState, clarificationQuestions,
    isLoading, error, submitTextOrder, submitVoiceOrder,
    answerClarification, skipClarification, confirmOrder, reportVoiceError, resetOrder
  } = useOrder()

  const customer = {
    customer_name: customerName.trim() || null,
    customer_phone: customerPhone.trim() || null,
    customer_address: customerAddress.trim() || null
  }
  const { isRecording, startRecording, stopRecording } = useVoiceRecorder({
    onTranscript: (audio) => submitVoiceOrder(audio, customer),
    onError: reportVoiceError
  })

  const submit = async () => {
    if (text.trim()) await submitTextOrder(text.trim(), customer)
  }

  const newOrder = () => {
    resetOrder()
    setText('')
    setCustomerName('')
    setCustomerPhone('')
    setCustomerAddress('')
  }

  return <>
    <PageHeader
      eyebrow="Live order workflow"
      title="AI Order Desk"
      subtitle="Create a customer order by text or voice, then download its confirmed bill."
      actions={<Button variant="ghost" icon="plus" onClick={newOrder}>New customer order</Button>}
    />

    <div className="ai-layout">
      <section className="card input-card">
        <div className="tabs">
          {['Text order', 'Voice order'].map((item) => <button className={`tab ${tab === item ? 'active' : ''}`} key={item} onClick={() => setTab(item)}>{item}</button>)}
        </div>

        <div className="input-row">
          <input className="input" value={customerName} onChange={(event) => setCustomerName(event.target.value)} placeholder="Customer name (optional)" />
          <input className="input" value={customerPhone} onChange={(event) => setCustomerPhone(event.target.value)} placeholder="WhatsApp / phone (optional)" />
        </div>
        <input className="input" style={{ marginTop: 10 }} value={customerAddress} onChange={(event) => setCustomerAddress(event.target.value)} placeholder="Delivery address (optional)" />

        {tab === 'Text order' ? <>
          <label className="field-label" htmlFor="order-message">Customer order</label>
          <textarea id="order-message" className="textarea" value={text} onChange={(event) => setText(event.target.value)} placeholder="e.g. bhaiya 2 kilo atta aur half kilo sugar dena" />
          <div className="helper"><Icon name="spark" size={15} /><span>Hindi, English, and Hinglish text are supported.</span></div>
          <div className="card-actions">
            <Button icon="spark" onClick={submit} disabled={isLoading || !text.trim()}>{isLoading ? 'Processing…' : 'Create order'}</Button>
            <Button variant="ghost" onClick={() => setText('')}>Clear</Button>
          </div>
        </> : <>
          <div className="voice-card">
            <div className={`mic-orb ${isRecording ? 'recording' : ''}`}><Icon name="mic" size={22} /></div>
            <strong>{isRecording ? 'Listening…' : 'Speak your customer order'}</strong>
            <p>{isRecording ? 'Tap stop when the customer is finished.' : (voiceState === 'ERROR' && error ? error : voiceMessages[voiceState])}</p>
            <Button variant={isRecording ? 'danger' : 'ai'} icon={isRecording ? 'check' : 'mic'} onClick={isRecording ? stopRecording : startRecording} disabled={isLoading}>
              {isRecording ? 'Stop recording' : 'Start recording'}
            </Button>
          </div>
          {transcript && <div className="quote" style={{ marginTop: 12 }}><strong>Transcript:</strong> {transcript}</div>}
        </>}

        {error && <div className="helper" style={{ background: 'var(--danger-soft)', color: '#ad6565', marginTop: 12 }}><Icon name="help" size={15} /><span>{error}</span></div>}
      </section>

      <section className="card analysis-card">
        <div className="analysis-title"><div><h2>Order status</h2><p>Only catalog-backed matches can be confirmed.</p></div><div className="ai-spark"><Icon name="spark" size={17} /></div></div>
        {isLoading && <div className="processing"><div className="processing-step"><span className="step-dot">…</span>Understanding customer order…</div><div className="processing-step"><span className="step-dot">…</span>Checking catalog and stock…</div></div>}
        {!isLoading && !order && <div className="summary-box"><div className="summary-row"><span>New order</span><b>Waiting for text or voice input</b></div></div>}
        {order && <>
          <div className="summary-box">
            <div className="summary-row"><span>Order ID</span><b>{order.id}</b></div>
            <div className="summary-row"><span>Customer</span><b>{order.customer_name || 'Walk-in customer'}</b></div>
            <div className="summary-row"><span>Status</span><StatusBadge status={status} /></div>
          </div>
          <div className="analysis-section-label">Matched products</div>
          {order.items.map((item) => <div className="match-card" key={item.id || item.product_name}>
            <div className="match-top"><div><strong>{item.product_name}</strong><small>{item.quantity} {item.unit}{item.brand ? ` · ${item.brand}` : ''}</small></div><b className="confidence">{Math.round((item.matched_confidence || 0) * 100)}%</b></div>
            <div className="match-meta"><span className="match-tag">Catalog matched</span><span className="match-confidence">₹{Number(item.line_total || item.quantity * item.unit_price).toFixed(2)}</span></div>
          </div>)}
          {status === 'pending' && !clarificationQuestions.length && <div className="analysis-actions"><Button onClick={confirmOrder} disabled={isLoading}>Confirm and create bill</Button></div>}
          {status === 'confirmed' && bill && <div className="analysis-actions"><Button icon="receipt" onClick={() => downloadBillPdf(order, bill)}>Download bill PDF</Button><Button variant="ghost" onClick={() => printBill(order, bill)}>Print bill</Button></div>}
        </>}
      </section>
    </div>

    {clarificationQuestions.length > 0 && <section className="card section-card" style={{ marginTop: 17, background: 'var(--warning-soft)', borderColor: '#f0d89e' }}>
      <div className="section-head"><div><h2>Clarification needed</h2><p>Select an available catalog option before confirming this customer order.</p></div><StatusBadge status="Pending clarification" /></div>
      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(230px,1fr))', gap: 10 }}>
        {clarificationQuestions.map((question, index) => <div key={`${question.code}-${index}`} className="clarification-card"><strong>{question.question}</strong><div className="candidate-list">{question.options?.map((option) => <button className="candidate" key={option} onClick={() => answerClarification(index, option)}>{option}</button>)}</div><button className="text-link" onClick={() => skipClarification(index)}>Skip item</button></div>)}
      </div>
    </section>}
  </>
}
