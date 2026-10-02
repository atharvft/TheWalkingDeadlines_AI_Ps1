"""FastAPI dependencies and safe demo database initialization."""

import json
import time
from pathlib import Path
from typing import Generator

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import Base
from app.db.database import SessionLocal, engine
from app.models.inventory import Inventory
from app.models.product import Product
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.services.billing_service import BillingService
from app.services.catalog_service import CatalogService
from app.services.clarification_service import ClarificationService
from app.services.inventory_service import InventoryService
from app.services.ai.ai_router import AIProviderRouter
from app.services.order_service import OrderService
from app.services.speech.transcription_service import TranscriptionService


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if session.query(Product).count() > 0:
            return
        normalized_path = _project_root() / "data" / "catalog" / "normalized_products.json"
        catalog_path = normalized_path if normalized_path.exists() else _project_root() / settings.catalog_path
        if not catalog_path.exists():
            raise FileNotFoundError(f"Catalog file not found: {catalog_path}")
        products = json.loads(catalog_path.read_text(encoding="utf-8"))
        for data in products:
            product = Product(
                id=str(data["id"]),
                name=data["name"],
                brand=data.get("brand"),
                category=data.get("category"),
                subcategory=data.get("subcategory"),
                unit=data.get("unit", "pcs"),
                pack_size=data.get("pack_size"),
                unit_price=float(data.get("unit_price", 0)),
                description=data.get("description"),
                aliases=json.dumps(data.get("aliases", [])),
                normalized_name=data.get("normalized_name", data["name"].lower()),
                source_product_id=data.get("source_product_id"),
                source_dataset=data.get("source_dataset", "curated_demo_fallback"),
                is_active=data.get("is_active", True),
            )
            session.add(product)
            session.add(Inventory(
                product_id=product.id,
                stock_quantity=float(data.get("stock_quantity", 100)),
                reserved_quantity=0,
                reorder_level=10,
                last_updated=int(time.time()),
            ))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_order_service() -> Generator[OrderService, None, None]:
    initialize_database()
    session: Session = SessionLocal()
    try:
        ai_router = AIProviderRouter()
        product_repo = ProductRepository(session)
        inventory_repo = InventoryRepository(session)
        yield OrderService(
            order_repo=OrderRepository(session),
            product_repo=product_repo,
            catalog_service=CatalogService(product_repo),
            inventory_service=InventoryService(inventory_repo),
            clarification_service=ClarificationService(),
            billing_service=BillingService(),
            ai_router=ai_router,
            transcription_service=TranscriptionService(ai_router),
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
