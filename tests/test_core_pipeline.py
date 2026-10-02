import pytest

from ai.nlp.normalization import hindi_audio_to_english_text, normalize_hinglish_text, normalize_unit
from ai.nlp.order_parser import OrderParser


def test_quantity_and_unit_normalization():
    assert normalize_hinglish_text("  AADHA   KILO, sugar!! ") == "aadha kilo, sugar"
    assert normalize_hinglish_text("भैया दो किलो आटा और आधा किलो चीनी देना") == "bhaiya 2 kilo atta aur aadha kilo cheeni dena"
    assert normalize_unit("litres") == "l"


def test_hindi_audio_transcript_is_converted_to_supported_english_grocery_text():
    assert hindi_audio_to_english_text("भैया दो किलो आटा और आधा किलो चीनी देना") == "2 kg wheat flour and 0.5 kg sugar please"


@pytest.mark.asyncio
async def test_hinglish_parser_extracts_multiple_items():
    parsed = await OrderParser().parse("bhaiya 2 kilo atta, aadha kilo sugar aur ek Amul butter dena")
    assert [(item.product_query, item.quantity, item.unit) for item in parsed.items] == [
        ("wheat flour", 2.0, "kg"),
        ("sugar", 0.5, "kg"),
        ("butter", 1.0, "pcs"),
    ]
    assert parsed.items[2].brand == "Amul"


@pytest.mark.asyncio
async def test_hindi_script_transcript_uses_the_hinglish_order_pipeline():
    parsed = await OrderParser().parse("भैया दो किलो आटा और आधा किलो चीनी देना")
    assert [(item.product_query, item.quantity, item.unit) for item in parsed.items] == [
        ("wheat flour", 2.0, "kg"),
        ("sugar", 0.5, "kg"),
    ]


@pytest.mark.asyncio
async def test_clean_order_confirm_and_bill(client):
    response = await client.post("/api/orders", json={"text": "bhaiya 2 kilo atta, aadha kilo sugar aur ek Amul butter dena"})
    assert response.status_code == 200
    order = response.json()
    assert order["status"] == "pending"
    assert len(order["items"]) == 3

    response = await client.post(f"/api/orders/{order['id']}/confirm")
    assert response.status_code == 200
    confirmed = response.json()
    assert confirmed["status"] == "confirmed"

    bill = (await client.get(f"/api/orders/{order['id']}/bill")).json()
    assert bill["subtotal"] == 399.0
    assert bill["tax"] == 71.82
    assert bill["total"] == 470.82


@pytest.mark.asyncio
async def test_clarification_persists_pending_oil_item(client):
    response = await client.post("/api/orders", json={"text": "bhaiya atta 2 kilo aur tel bhi chahiye"})
    data = response.json()
    assert data["status"] == "ambiguous"
    assert len(data["items"]) == 1
    assert data["clarification_questions"][0]["code"] == "MULTIPLE_CANDIDATES"

    answer = data["clarification_questions"][0]["options"][1]
    response = await client.post(
        f"/api/orders/{data['id']}/clarify",
        json={"question_index": 0, "answer": answer},
    )
    resolved = response.json()
    assert resolved["status"] == "pending"
    assert [item["product_name"] for item in resolved["items"]] == ["Wheat Flour", "Fortune Sunflower Oil"]


@pytest.mark.asyncio
async def test_pack_size_clarification_and_spelling_noise(client):
    response = await client.post("/api/orders", json={"text": "Fortune sunflower oil dena"})
    data = response.json()
    assert data["clarification_questions"][0]["code"] == "PACK_SIZE_UNKNOWN"
    response = await client.post(
        f"/api/orders/{data['id']}/clarify",
        json={"question_index": 0, "answer": "1L"},
    )
    assert response.json()["status"] == "pending"

    noisy = await client.post("/api/orders", json={"text": "amul buttr"})
    assert noisy.json()["items"][0]["product_name"] == "Amul Butter"


@pytest.mark.asyncio
async def test_stock_validation_is_deterministic(client):
    response = await client.post("/api/orders", json={"text": "1000 kg onions"})
    data = response.json()
    assert data["status"] == "ambiguous"
    question = data["clarification_questions"][0]
    assert question["code"] == "INSUFFICIENT_STOCK"
    assert "Only " in question["question"] and "1000" not in question["question"]
