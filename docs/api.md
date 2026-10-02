# Hinglish Order Desk - API Documentation

## Base URL

```
http://localhost:8000/api
```

## Endpoints

### Health Check

**GET** `/health`

Response:
```json
{
  "status": "ok",
  "service": "hinglish-order-desk"
}
```

### Transcription

**POST** `/transcription`

Upload audio file for speech-to-text.

Request: `multipart/form-data`
- `audio`: Audio file (webm, wav, mp3)

Response:
```json
{
  "text": "transcribed text",
  "confidence": 0.95
}
```

### Orders

#### Create Text Order

**POST** `/orders`

Request:
```json
{
  "text": "2 kg onions, 1 litre milk, 5 bananas"
}
```

Response:
```json
{
  "id": "order-123",
  "status": "pending|ambiguous|confirmed",
  "items": [
    {
      "product_name": "Onion",
      "brand": "Generic",
      "quantity": 2,
      "unit": "kg",
      "unit_price": 40.0,
      "line_total": 80.0
    }
  ],
  "clarification_questions": [
    {
      "question": "Did you mean 'Onion' for 'pyaz'?",
      "options": ["Yes", "No, different item"],
      "question_type": "product_match"
    }
  ]
}
```

#### Create Voice Order

**POST** `/orders/voice`

Request: `multipart/form-data`
- `audio`: Audio file

Response: Same as text order.

#### Get Order

**GET** `/orders/{order_id}`

Response: Full order details.

#### Answer Clarification

**POST** `/orders/{order_id}/clarify`

Request:
```json
{
  "question_index": 0,
  "answer": "Yes"
}
```

Response: Updated order.

#### Skip Clarification

**POST** `/orders/{order_id}/clarify/skip`

Request:
```json
{
  "question_index": 0
}
```

Response: Updated order.

#### Confirm Order

**POST** `/orders/{order_id}/confirm`

Response: Confirmed order with reserved inventory.

#### Get Bill

**GET** `/orders/{order_id}/bill`

Response:
```json
{
  "subtotal": 140.0,
  "tax": 25.2,
  "total": 165.2,
  "items": [...]
}
```

#### Get Delivery Note

**GET** `/orders/{order_id}/delivery-note`

Response:
```json
{
  "order_id": "order-123",
  "customer_name": "John",
  "customer_phone": "9876543210",
  "items": [...],
  "total": 165.2
}
```

### Clarifications

**GET** `/orders/{order_id}/clarifications`

Get pending clarification questions.

## Error Responses

All errors follow this format:
```json
{
  "detail": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

Common codes:
- `PRODUCT_NOT_FOUND` (404)
- `INSUFFICIENT_STOCK` (409)
- `AMBIGUITY_DETECTED` (422)
- `INVALID_ORDER_STATE` (400)
- `INTERNAL_ERROR` (500)