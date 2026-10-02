"""End-to-end order orchestration with persisted clarification state."""

import json
import logging
import re
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ai.matching.product_matcher import ProductMatcher
from ai.nlp.normalization import normalize_for_matching, normalize_unit
from ai.nlp.order_parser import OrderParser
from ai.schemas.ai import ParsedOrder, ParsedOrderItem
from ai.rules.quantity_rules import QuantityRules
from ai.rules.unit_rules import UnitRules

from app.core.exceptions import InsufficientStockError, OrderDeskException
from app.models.conversation_state import ConversationState
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import ClarificationQuestion, OrderItemResponse, OrderResponse
from app.schemas.ai import AIParsedOrder
from app.services.ai.ai_router import AIProviderRouter
from app.core.config import settings
from app.services.ai.errors import AIProviderError
from app.services.billing_service import BillingService
from app.services.catalog_service import CatalogService
from app.services.clarification_service import ClarificationService
from app.services.inventory_service import InventoryService
from app.services.speech.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        catalog_service: CatalogService,
        inventory_service: InventoryService,
        clarification_service: ClarificationService,
        billing_service: BillingService,
        asr_service=None,
        ai_router: Optional[AIProviderRouter] = None,
        transcription_service: Optional[TranscriptionService] = None,
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.catalog_service = catalog_service
        self.inventory_service = inventory_service
        self.clarification_service = clarification_service
        self.billing_service = billing_service
        self.asr_service = asr_service
        self.ai_router = ai_router or AIProviderRouter()
        self.transcription_service = transcription_service or TranscriptionService(self.ai_router)
        self.quantity_rules = QuantityRules()
        self.unit_rules = UnitRules()

    async def create_order_from_text(
        self,
        text: str,
        provider: Optional[str] = None,
        strict_ai: bool = False,
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None,
        customer_address: Optional[str] = None,
    ) -> dict:
        if not text or not text.strip():
            raise OrderDeskException("Order text cannot be empty", "INVALID_ORDER")
        try:
            ai_order = await self.ai_router.parse_order(text, provider=provider)
            parsed = self._business_order_from_ai(ai_order, text)
        except AIProviderError as exc:
            if strict_ai:
                logger.warning("[AI] structured extraction unavailable: %s", exc.__class__.__name__)
                raise OrderDeskException("AI processing is temporarily unavailable", "AI_UNAVAILABLE") from exc
            logger.warning("[AI] using deterministic parser fallback (%s)", exc.__class__.__name__)
            parsed = await OrderParser().parse(text)
        order_id = str(uuid.uuid4())
        now = int(time.time())
        order = Order(
            id=order_id,
            status=OrderStatus.PROCESSING,
            customer_name=customer_name or None,
            customer_phone=customer_phone or None,
            customer_address=customer_address or None,
            created_at=now,
            updated_at=now,
        )
        await self.order_repo.create(order)
        if not parsed.items:
            order.status = OrderStatus.REJECTED
            order.notes = "No grocery items could be extracted from the request."
            await self.order_repo.update(order)
            await self._save_state(order_id, parsed, [], [], "rejected", text)
            return self._process_response(order, [], transcript=text)
        return await self._resolve_and_persist(order, parsed, text)

    async def create_order_from_voice(
        self,
        audio_data: bytes,
        filename: str = "recording.webm",
        content_type: Optional[str] = "audio/webm",
        provider: Optional[str] = None,
    ) -> dict:
        try:
            transcription = await self.transcription_service.transcribe(
                audio_data, filename=filename, content_type=content_type, language=None
            )
        except AIProviderError as exc:
            raise OrderDeskException("Unable to transcribe audio. Please try again.", "TRANSCRIPTION_FAILED") from exc
        text = (transcription.get("transcript") or "").strip()
        if not text:
            raise OrderDeskException("The audio did not contain a usable transcript", "EMPTY_TRANSCRIPT")
        result = await self.create_order_from_text(text, provider=provider)
        result["transcript"] = text
        result["transcription_provider"] = transcription.get("provider", "openai")
        return result

    async def parse_order_with_ai(self, text: str, provider: Optional[str] = None) -> dict:
        if not text or not text.strip():
            raise OrderDeskException("Order text cannot be empty", "INVALID_ORDER")
        try:
            result = await self.ai_router.parse_order(text, provider=provider)
        except AIProviderError as exc:
            raise OrderDeskException("AI processing is temporarily unavailable", "AI_UNAVAILABLE") from exc
        return {"provider": self.ai_router.last_provider or (provider or settings.ai_provider).lower(), "parsed_order": self._dump(result)}

    @staticmethod
    def _business_order_from_ai(ai_order: AIParsedOrder, text: str) -> ParsedOrder:
        items = []
        for item in ai_order.items:
            quantity = item.quantity if item.quantity is not None else 1.0
            unit = normalize_unit(item.unit or "pcs")
            items.append(ParsedOrderItem(
                raw_text=item.raw_text or item.product,
                product_expression=item.product,
                product_query=normalize_for_matching(item.product),
                quantity=quantity,
                unit=unit,
                unit_explicit=item.unit is not None,
                quantity_explicit=item.quantity is not None,
                brand=item.brand,
                pack_size=item.pack_size,
            ))
        delivery = ai_order.delivery
        delivery_parts = [part for part in [delivery.date_text, delivery.time_text, delivery.address_text] if part]
        return ParsedOrder(
            items=items,
            normalized_text=normalize_for_matching(text),
            delivery_required=delivery.required,
            delivery_request=" ".join(delivery_parts) if delivery_parts else None,
            delivery_date_text=delivery.date_text,
            delivery_time_text=delivery.time_text,
            delivery_address_text=delivery.address_text,
            delivery_address=delivery.address_text,
        )

    async def get_order(self, order_id: str) -> Optional[dict]:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return None
        questions = await self._questions_for(order_id)
        return self._process_response(order, questions)

    async def answer_clarification(self, order_id: str, question_index: int, answer: str) -> dict:
        order, parsed, questions, state_data = await self._load_pending(order_id)
        if question_index < 0 or question_index >= len(questions):
            raise OrderDeskException("Clarification question not found", "QUESTION_NOT_FOUND")
        question = questions[question_index]
        item_index = question.get("item_index")
        if item_index is None or item_index >= len(parsed.items):
            raise OrderDeskException("Clarification item no longer exists", "QUESTION_STALE")
        item = parsed.items[item_index]
        code = question.get("code") or question.get("question_type")
        answer_text = (answer or "").strip()

        if code == "PACK_SIZE_UNKNOWN":
            selected = self._select_option(answer_text, question.get("candidates", []))
            pack = selected.get("pack_size") if selected else self._extract_pack(answer_text)
            if not pack:
                raise OrderDeskException("Please select a listed pack size", "INVALID_CLARIFICATION")
            item.pack_size = pack
            match = re.match(r"([\d.]+)\s*([a-z]+)", pack, re.I)
            if match:
                item.pack_size_value = float(match.group(1))
                item.pack_size_unit = normalize_unit(match.group(2))
        elif code in {"MULTIPLE_CANDIDATES", "PRODUCT_UNKNOWN", "BRAND_UNKNOWN"}:
            selected = self._select_option(answer_text, question.get("candidates", []))
            if selected:
                item.product_query = normalize_for_matching(selected.get("product_name", ""))
                item.product_expression = selected.get("product_name", item.product_expression)
                item.brand = selected.get("brand") or item.brand
                item.pack_size = selected.get("pack_size") or item.pack_size
            else:
                item.product_query = normalize_for_matching(answer_text)
        elif code in {"OUT_OF_STOCK", "INSUFFICIENT_STOCK"}:
            lowered = answer_text.lower()
            substitute = self._select_option(answer_text, question.get("substitutes", []))
            if substitute:
                item.product_query = normalize_for_matching(substitute.get("product_name", ""))
                item.product_expression = substitute.get("product_name", item.product_expression)
                item.brand = substitute.get("brand")
                item.pack_size = substitute.get("pack_size")
            elif lowered.startswith(("no", "remove", "skip")):
                parsed.items.pop(item_index)
            elif lowered.startswith(("yes", "use", "available")):
                available = float(question.get("available", 0))
                item.quantity = available
            else:
                try:
                    item.quantity = float(answer_text)
                except ValueError as exc:
                    raise OrderDeskException("Answer yes, no, or provide a quantity", "INVALID_CLARIFICATION") from exc
        elif code == "UNIT_MISMATCH":
            if answer_text.lower().startswith(("no", "change")):
                raise OrderDeskException("Please provide a compatible unit", "INVALID_CLARIFICATION")

        history = state_data.get("clarification_history", [])
        history.append({"question_index": question_index, "question": question.get("question"), "answer": answer_text})
        return await self._resolve_and_persist(order, parsed, state_data.get("raw_text", ""), history=history)

    async def skip_clarification(self, order_id: str, question_index: int) -> dict:
        order, parsed, questions, state_data = await self._load_pending(order_id)
        if question_index < 0 or question_index >= len(questions):
            raise OrderDeskException("Clarification question not found", "QUESTION_NOT_FOUND")
        item_index = questions[question_index].get("item_index")
        if item_index is not None and item_index < len(parsed.items):
            parsed.items.pop(item_index)
        history = state_data.get("clarification_history", [])
        history.append({"question_index": question_index, "answer": "skipped"})
        return await self._resolve_and_persist(order, parsed, state_data.get("raw_text", ""), history=history)

    async def confirm_order(self, order_id: str) -> dict:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderDeskException("Order not found", "ORDER_NOT_FOUND")
        questions = await self._questions_for(order_id)
        if questions:
            raise OrderDeskException("Resolve the pending clarification first", "CLARIFICATION_REQUIRED")
        if order.status == OrderStatus.CONFIRMED:
            return self._process_response(order, [])
        if order.status != OrderStatus.PENDING:
            raise OrderDeskException("Order cannot be confirmed in current state", "INVALID_ORDER_STATE")

        issues = await self.inventory_service.validate_order_items(order.items)
        if issues:
            raise OrderDeskException("Some items are no longer available", "INSUFFICIENT_STOCK", issues)
        try:
            await self.inventory_service.reserve_stock(order.items)
        except InsufficientStockError as exc:
            raise OrderDeskException(str(exc), "INSUFFICIENT_STOCK") from exc
        bill = await self.billing_service.calculate_bill(order)
        now = int(time.time())
        order.status = OrderStatus.CONFIRMED
        order.subtotal = bill.subtotal
        order.tax = bill.tax
        order.total_amount = bill.total
        order.confirmed_at = now
        order.updated_at = now
        await self.order_repo.update(order)
        return self._process_response(order, [])

    async def get_bill(self, order_id: str) -> dict:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderDeskException("Order not found", "ORDER_NOT_FOUND")
        if order.status != OrderStatus.CONFIRMED:
            raise OrderDeskException("Confirm the order before requesting a bill", "ORDER_NOT_CONFIRMED")
        bill = await self.billing_service.calculate_bill(order)
        return {
            "order_id": order.id,
            "items": self._bill_items(order),
            "subtotal": bill.subtotal,
            "tax": bill.tax,
            "tax_rate": bill.tax_rate,
            "total": bill.total,
        }

    async def get_delivery_note(self, order_id: str) -> dict:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderDeskException("Order not found", "ORDER_NOT_FOUND")
        if order.status != OrderStatus.CONFIRMED:
            raise OrderDeskException("Confirm the order before requesting a delivery note", "ORDER_NOT_CONFIRMED")
        return await self.billing_service.generate_delivery_note(order)

    async def get_clarifications(self, order_id: str) -> List[ClarificationQuestion]:
        return [ClarificationQuestion(**question) for question in await self._questions_for(order_id)]

    async def _resolve_and_persist(self, order: Order, parsed: ParsedOrder, raw_text: str, history=None) -> dict:
        catalog = await self.catalog_service.get_matching_catalog()
        matcher = ProductMatcher(catalog)
        questions: List[dict] = []
        selected: List[dict] = []
        order.items.clear()
        validation_errors = []

        for index, item in enumerate(parsed.items):
            item_errors = self._item_validation_errors(index, item)
            validation_errors.extend(item_errors)
            if item_errors:
                continue
            candidates = matcher.match(item)
            if item.pack_size:
                filtered = [candidate for candidate in candidates if self._same_pack(candidate.pack_size, item.pack_size)]
                if filtered:
                    candidates = filtered
            if not candidates:
                unbranded = item.model_copy(update={"brand": None}) if hasattr(item, "model_copy") else item.copy(update={"brand": None})
                alternatives = matcher.match(unbranded) if item.brand else []
                code = "BRAND_UNKNOWN" if item.brand and alternatives else "PRODUCT_UNKNOWN"
                questions.append(self._question_for_product(index, item, alternatives or candidates, code))
                continue
            if item.pack_size and not any(self._same_pack(candidate.pack_size, item.pack_size) for candidate in candidates):
                questions.append(self._question_for_pack(index, item, candidates))
                continue
            if len(candidates) > 1:
                same_name = len({normalize_for_matching(candidate.product_name) for candidate in candidates}) == 1
                if item.pack_size is None and same_name:
                    questions.append(self._question_for_pack(index, item, candidates))
                else:
                    questions.append(self._question_for_product(index, item, candidates, "MULTIPLE_CANDIDATES"))
                continue

            candidate = candidates[0]
            if item.unit_explicit and not self.unit_rules.are_compatible(item.unit, candidate.unit):
                questions.append({
                    "question": f"{candidate.product_name} is sold in {candidate.unit}. Continue with that unit?",
                    "options": ["Yes, continue", "No, change unit"],
                    "question_type": "unit_mismatch", "code": "UNIT_MISMATCH", "item_index": index,
                    "candidates": [self._candidate_dict(candidate)],
                })
                continue
            available = await self.inventory_service.get_available_quantity(candidate.product_id)
            requested_quantity = float(item.quantity or 0)
            if available < requested_quantity:
                substitutes = await self._find_substitutes(candidate, item, catalog)
                substitute_text = ""
                if substitutes:
                    substitute_text = " Available alternatives: " + ", ".join(item["product_name"] for item in substitutes) + "."
                questions.append({
                    "question": f"Only {available:g} {candidate.unit} of {candidate.product_name} is available.{substitute_text} Use available quantity?",
                    "options": ["Yes, use available", "No, remove item", "Change quantity"],
                    "question_type": "stock", "code": "OUT_OF_STOCK" if available == 0 else "INSUFFICIENT_STOCK",
                    "item_index": index, "available": available, "requested": requested_quantity,
                    "candidates": [self._candidate_dict(candidate)], "substitutes": substitutes, "suggestions": substitutes,
                })
                continue
            product = await self.product_repo.get_by_id(candidate.product_id)
            if not product:
                validation_errors.append(f"Product {candidate.product_id} disappeared from catalog")
                continue
            line_total = round(requested_quantity * float(product.unit_price), 2)
            order.items.append(OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                brand=product.brand,
                quantity=requested_quantity,
                unit=product.unit,
                unit_price=product.unit_price,
                line_total=line_total,
                matched_confidence=candidate.confidence,
            ))
            selected.append(self._candidate_dict(candidate))

        order.status = OrderStatus.AMBIGUOUS if questions or validation_errors else OrderStatus.PENDING
        order.notes = parsed.delivery_request or None
        order.subtotal = 0
        order.tax = 0
        order.total_amount = 0
        order.updated_at = int(time.time())
        await self.order_repo.update(order)
        await self._save_state(order.id, parsed, selected, questions, "clarification_needed" if questions else order.status.value, raw_text, history or [])
        return self._process_response(order, [ClarificationQuestion(**question) for question in questions], evidence=selected)

    def _item_validation_errors(self, index: int, item: ParsedOrderItem) -> List[str]:
        issues = []
        if item.quantity is None:
            issues.append(f"Item {index + 1}: quantity is missing")
        elif item.quantity <= 0:
            issues.append(f"Item {index + 1}: quantity must be positive")
        if item.quantity is not None and item.quantity > QuantityRules.MAX_QUANTITY:
            issues.append(f"Item {index + 1}: quantity exceeds {QuantityRules.MAX_QUANTITY}")
        if not item.product_query:
            issues.append(f"Item {index + 1}: product is missing")
        return issues

    async def _load_pending(self, order_id: str) -> Tuple[Order, ParsedOrder, List[dict], dict]:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderDeskException("Order not found", "ORDER_NOT_FOUND")
        state = await self.order_repo.get_conversation_state(order_id)
        if not state or not state.parsed_data:
            raise OrderDeskException("No clarification is pending", "NO_CLARIFICATION")
        data = state.parsed_data
        parsed_data = data.get("parsed_order", data)
        parsed = ParsedOrder(**parsed_data)
        questions = data.get("questions", [])
        return order, parsed, questions, data

    async def _save_state(self, order_id, parsed, selected, questions, step, raw_text, history=None):
        existing = await self.order_repo.get_conversation_state(order_id)
        state = existing or ConversationState(order_id=order_id, current_step=step, updated_at=int(time.time()))
        state.current_step = step
        state.parsed_data = {
            "parsed_order": self._dump(parsed),
            "questions": questions,
            "raw_text": raw_text,
            "clarification_history": history or [],
        }
        state.matched_products = selected
        state.clarification_history = history or []
        state.awaiting_question_index = 0 if questions else None
        state.updated_at = int(time.time())
        await self.order_repo.save_conversation_state(state)

    async def _questions_for(self, order_id: str) -> List[dict]:
        state = await self.order_repo.get_conversation_state(order_id)
        return (state.parsed_data or {}).get("questions", []) if state else []

    @staticmethod
    def _dump(value):
        if hasattr(value, "model_dump"):
            return value.model_dump()
        return value.dict()

    @staticmethod
    def _candidate_dict(candidate) -> dict:
        return {
            "product_id": candidate.product_id,
            "product_name": candidate.product_name,
            "brand": candidate.brand,
            "category": candidate.category,
            "unit": candidate.unit,
            "unit_price": candidate.unit_price,
            "pack_size": candidate.pack_size,
            "confidence": candidate.confidence,
            "match_type": candidate.match_type,
            "reason": candidate.reason,
        }

    def _question_for_pack(self, index, item, candidates):
        options = [candidate.pack_size or candidate.unit for candidate in candidates]
        return {
            "question": f"Which pack size would you like for {item.brand + ' ' if item.brand else ''}{item.product_query}?",
            "options": list(dict.fromkeys(options)), "question_type": "pack_size", "code": "PACK_SIZE_UNKNOWN",
            "item_index": index, "candidates": [self._candidate_dict(c) for c in candidates],
        }

    def _question_for_product(self, index, item, candidates, code):
        options = [f"{c.product_name}{' ' + c.pack_size if c.pack_size else ''}{' (' + c.brand + ')' if c.brand else ''}" for c in candidates]
        wording = f"Which {item.product_query or 'product'} would you like?" if code != "BRAND_UNKNOWN" else f"We don't have {item.brand} {item.product_query}. Choose an available option:"
        return {
            "question": wording, "options": list(dict.fromkeys(options)) or ["Type the product name"],
            "question_type": "product", "code": code, "item_index": index,
            "candidates": [self._candidate_dict(c) for c in candidates],
        }

    async def _find_substitutes(self, candidate, requested, catalog) -> List[dict]:
        """Suggest only in-stock same-category, same-unit catalog rows."""
        suggestions = []
        for product in catalog:
            if product["id"] == candidate.product_id or product.get("category") != candidate.category:
                continue
            if not self.unit_rules.are_compatible(product.get("unit", "pcs"), candidate.unit):
                continue
            if await self.inventory_service.get_available_quantity(product["id"]) < requested.quantity:
                continue
            price = float(product.get("unit_price", 0))
            if candidate.unit_price and abs(price - candidate.unit_price) / candidate.unit_price > 0.75:
                continue
            suggestions.append({
                "product_id": product["id"], "product_name": product["name"], "brand": product.get("brand"),
                "pack_size": product.get("pack_size"), "unit": product.get("unit"), "unit_price": price,
                "reason": f"same category ({candidate.category}), compatible unit, and currently available",
            })
        return suggestions[:3]

    @staticmethod
    def _same_pack(left: Optional[str], right: Optional[str]) -> bool:
        return bool(left and right and normalize_for_matching(left) == normalize_for_matching(right))

    @staticmethod
    def _extract_pack(text: str) -> Optional[str]:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kilo|g|gram|l|litre|liter|ml|pcs?|pack|packet|bottle|box)\b", text, re.I)
        if not match:
            return None
        return f"{float(match.group(1)):g}{normalize_unit(match.group(2))}"

    @staticmethod
    def _select_option(answer: str, candidates: List[dict]) -> Optional[dict]:
        normalized_answer = normalize_for_matching(answer)
        for candidate in candidates:
            values = [candidate.get("pack_size"), candidate.get("product_name")]
            if any(value and normalize_for_matching(str(value)) in normalized_answer for value in values):
                return candidate
        for candidate in candidates:
            brand = candidate.get("brand")
            if brand and normalize_for_matching(str(brand)) == normalized_answer:
                return candidate
        return None

    def _process_response(self, order: Order, questions: List[ClarificationQuestion], transcript=None, evidence=None) -> dict:
        response = self._to_response(order)
        order_data = self._dump(response)
        return {
            "order": order_data,
            "id": order_data["id"],
            "status": order_data["status"],
            "items": order_data["items"],
            "clarification_questions": [self._dump(question) for question in questions],
            "transcript": transcript,
            "evidence": evidence or [],
        }

    def _to_response(self, order: Order) -> OrderResponse:
        return OrderResponse(
            id=order.id,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_address=order.customer_address,
            status=order.status.value if hasattr(order.status, "value") else str(order.status),
            items=[OrderItemResponse(
                id=item.id,
                product_name=item.product_name,
                brand=item.brand,
                quantity=float(item.quantity),
                unit=item.unit,
                unit_price=float(item.unit_price),
                line_total=float(item.line_total),
                matched_confidence=float(item.matched_confidence) if item.matched_confidence is not None else None,
            ) for item in order.items],
            subtotal=float(order.subtotal or 0),
            tax=float(order.tax or 0),
            total_amount=float(order.total_amount or 0),
            notes=order.notes,
            created_at=datetime.fromtimestamp(order.created_at),
            updated_at=datetime.fromtimestamp(order.updated_at),
            confirmed_at=datetime.fromtimestamp(order.confirmed_at) if order.confirmed_at else None,
        )

    @staticmethod
    def _bill_items(order):
        return [{
            "product_name": item.product_name, "brand": item.brand, "quantity": float(item.quantity),
            "unit": item.unit, "unit_price": float(item.unit_price), "line_total": round(float(item.quantity) * float(item.unit_price), 2),
        } for item in order.items]
