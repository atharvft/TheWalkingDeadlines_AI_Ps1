from typing import List, Dict
import numpy as np


class SemanticMatcher:
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", threshold: float = 0.5):
        self.threshold = threshold
        self.model = None
        self.catalog_embeddings = None
        self.catalog_products = None
        self.model_name = model_name
        self._available = False

    def _load_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                self._available = True
            except ImportError:
                self._available = False

    def index_catalog(self, catalog: List[Dict]):
        if not self._available:
            return
        self._load_model()
        self.catalog_products = catalog
        texts = [f"{p.get('name', '')} {p.get('brand', '')} {p.get('category', '')}" for p in catalog]
        self.catalog_embeddings = self.model.encode(texts, convert_to_numpy=True)

    def match(self, query: str, catalog: List[Dict]) -> List[Dict]:
        if not self._available:
            return []
        
        if self.catalog_products is None or self.catalog_products != catalog:
            self.index_catalog(catalog)

        if not catalog:
            return []

        self._load_model()
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        similarities = np.dot(self.catalog_embeddings, query_embedding.T).flatten()
        top_indices = np.argsort(similarities)[::-1][:10]

        matches = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= self.threshold:
                product = catalog[idx]
                matches.append({
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "brand": product.get("brand"),
                    "unit": product["unit"],
                    "unit_price": product["unit_price"],
                    "score": score,
                    "match_type": "semantic"
                })

        return matches