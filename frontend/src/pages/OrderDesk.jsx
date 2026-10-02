import { useState } from 'react'
import OrderInput from '../components/order/OrderInput'
import VoiceRecorder from '../components/order/VoiceRecorder'
import OrderItems from '../components/order/OrderItems'
import OrderStatus from '../components/order/OrderStatus'
import ClarificationPanel from '../components/order/ClarificationPanel'
import BillSummary from '../components/bill/BillSummary'
import DeliveryNote from '../components/bill/DeliveryNote'
import Loader from '../components/common/Loader'
import ErrorMessage from '../components/common/ErrorMessage'
import Button from '../components/common/Button'
import { useOrder } from '../hooks/useOrder'
import { useVoiceRecorder } from '../hooks/useVoiceRecorder'

export default function OrderDesk() {
  const {
    order,
    status,
    clarificationQuestions,
    error,
    isLoading,
    submitTextOrder,
    submitVoiceOrder,
    answerClarification,
    skipClarification,
    confirmOrder,
    resetOrder,
    voiceState,
    transcript
  } = useOrder()

  const { isRecording, startRecording, stopRecording } = useVoiceRecorder({
    onTranscript: submitVoiceOrder
  })

  const [inputValue, setInputValue] = useState('')

  const handleTextSubmit = () => {
    if (inputValue.trim()) {
      submitTextOrder(inputValue.trim())
      setInputValue('')
    }
  }

  const handleVoiceStart = () => startRecording()
  const handleVoiceStop = () => stopRecording()

  if (!order && status === 'pending') {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-2xl mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Hinglish Order Desk</h1>
            <p className="text-gray-600 mt-2">Enter your grocery order in text or voice</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-8 space-y-6">
            <OrderInput
              value={inputValue}
              onChange={setInputValue}
              onSubmit={handleTextSubmit}
              placeholder="Type your order here... (e.g., '2 kg onions, 1 litre milk, 5 bananas')"
              disabled={isLoading}
            />
            <div className="flex justify-center">
              <VoiceRecorder
                onStart={handleVoiceStart}
                onStop={handleVoiceStop}
                isRecording={isRecording}
                disabled={isLoading}
              />
            </div>
            {voiceState !== 'IDLE' && (
              <p className="text-center text-sm text-gray-600" role="status">
                {{
                  UPLOADING: 'Uploading audio…',
                  TRANSCRIBING: 'Transcribing your order…',
                  PROCESSING_ORDER: 'Understanding order and checking products…',
                  SUCCESS: 'Order understood.',
                  ERROR: 'Voice processing failed. Please try again.'
                }[voiceState] || 'Ready'}
              </p>
            )}
            {transcript && (
              <p className="rounded-lg bg-gray-50 px-4 py-3 text-sm text-gray-700">
                <span className="font-medium">Transcript:</span> {transcript}
              </p>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Order Desk</h1>
          <OrderStatus status={status} />
        </div>

        <ErrorMessage message={error} onDismiss={() => {}} />

        {clarificationQuestions?.length > 0 && (
          <ClarificationPanel
            questions={clarificationQuestions}
            onAnswer={answerClarification}
            onSkip={skipClarification}
          />
        )}

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">Order Items</h2>
          {isLoading ? (
            <div className="flex justify-center py-8"><Loader /></div>
          ) : (
            <OrderItems
              items={order?.items}
              onUpdateQuantity={(idx, qty) => {}}
              onRemove={(idx) => {}}
              readOnly={status !== 'pending' && status !== 'ambiguous'}
            />
          )}
        </div>

        {order && (
          <>
            <BillSummary order={order} />
            {status === 'confirmed' && (
              <DeliveryNote order={order} shopInfo={{ name: 'Demo Shop', address: '123 Market St', phone: '9876543210' }} />
            )}
          </>
        )}

        {status === 'confirmed' && (
          <div className="flex justify-center">
            <Button onClick={resetOrder} variant="secondary">New Order</Button>
          </div>
        )}

        {status === 'pending' && order && (
          <div className="flex justify-center">
            <Button onClick={confirmOrder} variant="primary" disabled={isLoading}>
              {isLoading ? <Loader size="sm" /> : 'Confirm Order'}
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
