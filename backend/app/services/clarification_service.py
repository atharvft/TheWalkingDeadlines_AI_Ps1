from typing import List, Optional
from app.schemas.ai import ParsedOrderItem
from app.schemas.order import ClarificationQuestion


class ClarificationService:
    def __init__(self):
        pass

    async def generate_questions(
        self,
        parsed_items: List[ParsedOrderItem],
        matched_products: List[dict],
        stock_issues: List[dict]
    ) -> List[ClarificationQuestion]:
        questions = []

        for issue in stock_issues:
            questions.append(ClarificationQuestion(
                question=f"Only {issue['available']} {issue.get('unit', 'units')} of {issue['product_name']} available. Requested {issue['requested']}. Proceed with available quantity?",
                options=["Yes, use available", "No, remove item", "Change quantity"],
                question_type="stock"
            ))

        for i, (parsed, matched) in enumerate(zip(parsed_items, matched_products)):
            if matched.get("confidence", 1.0) < 0.8:
                options = [f"{m['product_name']} ({m.get('brand', '')})" for m in matched.get("alternatives", [])]
                options.append("None of these")
                questions.append(ClarificationQuestion(
                    question=f"Did you mean '{matched['product_name']}' for '{parsed.product_expression}'?",
                    options=options,
                    question_type="product_match"
                ))

            if not matched.get("unit_match", True):
                questions.append(ClarificationQuestion(
                    question=f"'{parsed.product_expression}' uses '{parsed.unit}' but matched product uses '{matched.get('unit')}'. Continue?",
                    options=["Yes, continue", "No, change unit"],
                    question_type="unit_mismatch"
                ))

        return questions

    async def process_answer(
        self,
        question_index: int,
        answer: str,
        parsed_order,
        matched_products: List[dict]
    ) -> dict:
        # TODO: Process clarification answer and return updated order state
        return {"question_index": question_index, "answer": answer, "processed": True}