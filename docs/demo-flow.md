# Hinglish Order Desk - Demo Flow

## Hackathon Demo Journey

This document outlines the demonstration flow for the hackathon presentation.

## Demo Scenarios

### Scenario 1: Simple Hinglish Text Order (Happy Path)

**Input**: "do kilo pyaz aur ek litre doodh, paanch kela"

**Expected Flow**:
1. User types Hinglish order in text input
2. System parses: 2 kg onion, 1 litre milk, 5 bananas
3. Products matched with high confidence (>0.9)
4. Inventory validated (all in stock)
5. Order confirmed automatically
6. Bill generated: ₹185 (onions ₹80 + milk ₹60 + bananas ₹25 + 18% tax)
7. Delivery note displayed

**Key Demo Points**:
- Hinglish understanding (Hindi + English mixed)
- Alias matching (pyaz → onion, doodh → milk, kela → banana)
- Unit normalization (kilo → kg, litre → litre)
- Number word parsing (do → 2, ek → 1, paanch → 5)

---

### Scenario 2: English Text Order

**Input**: "2 kg onions, 1 litre milk, 5 bananas"

**Expected Flow**: Same as Scenario 1 but with English input.

**Key Demo Points**:
- Pure English also works
- Consistent parsing regardless of language

---

### Scenario 3: Voice Order (ASR + NLP)

**Input**: User speaks "teen kilo tamatar, adha kilo mirch, ek dozen anda"

**Expected Flow**:
1. User clicks record button
2. Speaks order in Hinglish
3. ASR transcribes to text
4. NLP parses: 3 kg tomato, 0.5 kg chilli, 1 dozen eggs
5. Products matched and validated
6. Order confirmed
7. Bill: ₹146.50 (tomatoes ₹90 + chilli ₹15 + eggs ₹30 + tax)

**Key Demo Points**:
- End-to-end voice pipeline
- Hindi number words (teen → 3, adha → 0.5, ek → 1)
- Unit handling (dozen for eggs)

---

### Scenario 4: Ambiguity Resolution (Clarification)

**Input**: "patanjali atta 2 kg" (but catalog has Aashirvaad brand)

**Expected Flow**:
1. System matches with low confidence (brand mismatch)
2. Clarification panel appears: "Requested Patanjali but matched Aashirvaad. Continue?"
3. Options: [Yes, use Aashirvaad] [No, remove] [Change quantity]
4. User selects "Yes, use Aashirvaad"
5. Order proceeds with matched product

**Key Demo Points**:
- Ambiguity detection
- Brand mismatch handling
- Interactive clarification UI
- User control over resolution

---

### Scenario 5: Low Stock Handling

**Input**: "10 kg onions" (inventory only has 5 kg)

**Expected Flow**:
1. System detects insufficient stock
2. Clarification: "Only 5 kg onions available. Requested 10. Proceed with 5?"
3. Options: [Yes, use 5 kg] [No, remove] [Change quantity]
4. User selects quantity adjustment
5. Order confirmed with available stock

**Key Demo Points**:
- Real-time inventory checking
- Stock validation before confirmation
- Graceful handling of shortages

---

### Scenario 6: Unit Mismatch

**Input**: "1 kg milk" (milk sold in litres)

**Expected Flow**:
1. System detects unit mismatch (kg vs litre)
2. Clarification: "Milk sold in litres. Continue with 1 litre?"
3. User confirms
4. Order proceeds with corrected unit

**Key Demo Points**:
- Unit validation rules
- Smart unit suggestions
- Category-aware unit checking

---

## Demo Script (5 minutes)

| Time | Action | Screen |
|------|--------|--------|
| 0:00 | Open app, show empty state | OrderDesk |
| 0:15 | Type "do kilo pyaz aur ek litre doodh" | Text input |
| 0:30 | Show parsed items with confidence | OrderItems |
| 0:45 | Click Confirm | Button |
| 1:00 | Show bill & delivery note | BillSummary, DeliveryNote |
| 1:30 | Click "New Order" | Reset |
| 1:45 | Click Voice Record, speak "teen kilo tamatar" | VoiceRecorder |
| 2:15 | Show transcript → parsed → matched | All panels |
| 2:45 | Confirm, show bill | BillSummary |
| 3:00 | New order: "patanjali atta 2 kg" | Text input |
| 3:15 | Show clarification panel | ClarificationPanel |
| 3:30 | Select option, confirm | Button |
| 3:45 | Show bill with Aashirvaad | BillSummary |
| 4:00 | Quick summary of architecture | Terminal/Slides |

---

## Technical Highlights to Mention

1. **Modular Monorepo**: Clean separation (frontend, backend, AI, data, tests)
2. **AI/Backend Separation**: AI understands language; backend owns truth (prices, stock)
3. **Layered Backend**: API → Service → Repository → Database
4. **Static vs Runtime Data**: Catalog in `data/`, DB in `backend/data/`
5. **Deterministic Billing**: Prices from DB, not LLM
6. **Extensible Rules**: Ambiguity, stock, quantity, unit as separate modules
7. **Conversation State**: Persistent clarification handling