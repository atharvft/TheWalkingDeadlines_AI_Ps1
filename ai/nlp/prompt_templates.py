ORDER_PARSING_PROMPT = """
Parse the following Hinglish grocery order into structured JSON.

Text: "{text}"

Extract:
1. Items with: product_expression (original text), quantity, unit, brand (if mentioned), modifiers
2. Delivery address (if mentioned)
3. Customer name (if mentioned)
4. Customer phone (if mentioned)
5. Special instructions (if any)

Return JSON only:
{{
  "items": [
    {{
      "product_expression": "string",
      "quantity": number,
      "unit": "string",
      "brand": "string or null",
      "modifiers": ["string"]
    }}
  ],
  "delivery_address": "string or null",
  "customer_name": "string or null",
  "customer_phone": "string or null",
  "special_instructions": "string or null"
}}
"""

CLARIFICATION_PROMPT = """
The user's order has ambiguities. Generate clarification questions.

Ambiguities: {ambiguities}

Return JSON array of questions:
[
  {{
    "question": "string",
    "options": ["string"],
    "question_type": "string"
  }}
]
"""

MATCHING_PROMPT = """
Match customer expression to product catalog.

Customer expression: "{expression}"
Catalog products: {products}

Return best match with confidence.
"""