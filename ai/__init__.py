# AI/ML Modules for Hinglish Order Desk

from ai.nlp.order_parser import OrderParser
from ai.matching.product_matcher import ProductMatcher
from ai.rules.ambiguity import AmbiguityDetector
from ai.rules.stock_rules import StockRules
from ai.rules.quantity_rules import QuantityRules
from ai.rules.unit_rules import UnitRules

try:
    from ai.asr.whisper_service import WhisperService
except ImportError:
    WhisperService = None

__all__ = [
    "OrderParser",
    "ProductMatcher",
    "AmbiguityDetector",
    "StockRules",
    "QuantityRules",
    "UnitRules"
]

if WhisperService:
    __all__.append("WhisperService")