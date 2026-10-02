ORDER_SYSTEM_PROMPT = """You extract grocery orders from Hinglish, Hindi-English, or English text.
Return only the requested JSON schema. Preserve uncertainty with null values.
Extract language facts only: product wording, brand, quantity, unit, pack size, and delivery instructions.
Never invent a SKU, product ID, price, stock status, availability, or catalog item.
Use null for missing quantity, unit, brand, or pack size. Normalize words such as aadha, paav, dedh,
sawa, dhai, and dozen only when their meaning is clear. Keep each item's original phrase in raw_text.
"""


def clarification_prompt(context: str, options: list[str]) -> str:
    joined = ", ".join(options)
    return f"""Generate one short Hinglish clarification for this order context:
{context}

Only use these database-backed options, and do not add any option not in the list:
{joined}

Return only the requested JSON schema with a concise question and the options used."""
