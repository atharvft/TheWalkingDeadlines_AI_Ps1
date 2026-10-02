import pytest
from httpx import AsyncClient


class TestOrderFlow:
    @pytest.mark.asyncio
    async def test_text_order_flow(self, client: AsyncClient):
        # 1. Submit text order
        response = await client.post("/api/orders", json={"text": "2 kg onions, 1 litre milk"})
        assert response.status_code == 200
        order = response.json()
        assert "id" in order
        assert order["status"] in ["pending", "processing", "ambiguous"]

        # 2. If ambiguous, answer clarifications
        if order["status"] == "ambiguous":
            for i, q in enumerate(order.get("clarification_questions", [])):
                response = await client.post(
                    f"/api/orders/{order['id']}/clarify",
                    json={"question_index": i, "answer": q["options"][0] if q["options"] else "yes"}
                )
                assert response.status_code == 200

        # 3. Confirm order
        response = await client.post(f"/api/orders/{order['id']}/confirm")
        assert response.status_code == 200
        confirmed = response.json()
        assert confirmed["status"] == "confirmed"

        # 4. Get bill
        response = await client.get(f"/api/orders/{order['id']}/bill")
        assert response.status_code == 200
        bill = response.json()
        assert "total" in bill

        # 5. Get delivery note
        response = await client.get(f"/api/orders/{order['id']}/delivery-note")
        assert response.status_code == 200
        note = response.json()
        assert "order_id" in note

    @pytest.mark.asyncio
    async def test_invalid_order(self, client: AsyncClient):
        response = await client.post("/api/orders", json={"text": ""})
        assert response.status_code == 400