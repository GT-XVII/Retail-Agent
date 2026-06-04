"""Catalog data access service for the Retail Agent."""

import json
import re
from pathlib import Path


STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "i",
    "in",
    "me",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


class CatalogService:
    """Load and query the local demo product catalog."""

    def __init__(self, catalog_path=None):
        self.catalog_path = Path(catalog_path or "data/electronics_demo_products.json")
        self.products = self._load_products()

    def _load_products(self):
        if not self.catalog_path.exists():
            return []

        with open(self.catalog_path, "r", encoding="utf-8") as catalog_file:
            return json.load(catalog_file)

    def search(self, query, limit=None):
        query = query.strip().lower()

        if not query:
            results = self.products
        else:
            scored_results = [
                (self._score_product(product, query), product)
                for product in self.products
            ]
            results = [
                product
                for score, product in sorted(
                    scored_results,
                    key=lambda result: (
                        result[0],
                        result[1].get("average_rating", 0),
                        result[1].get("rating_number", 0),
                    ),
                    reverse=True,
                )
                if score > 0
            ]

        if limit is None:
            return results

        return results[:limit]

    def _score_product(self, product, query):
        query_terms = self._tokenize(query)

        if not query_terms:
            return 0

        weighted_fields = [
            ("title", 40),
            ("brand", 25),
            ("category", 20),
            ("features", 8),
            ("description", 4),
        ]
        score = 0

        for field_name, weight in weighted_fields:
            value = self._field_text(product, field_name)

            if not value:
                continue

            field_terms = set(self._tokenize(value, remove_stop_words=False))

            if query in value:
                score += weight * 3

            for term in query_terms:
                if term in field_terms:
                    score += weight
                elif term in value:
                    score += max(1, weight // 4)

        return score

    def _field_text(self, product, field_name):
        value = product.get(field_name)

        if value is None:
            return ""

        if isinstance(value, list):
            value = " ".join(str(item) for item in value if item is not None)

        return str(value).lower()

    def _tokenize(self, value, remove_stop_words=True):
        tokens = re.findall(r"[a-z0-9]+", value.lower())
        tokens = [token for token in tokens if len(token) > 1]

        if not remove_stop_words:
            return tokens

        return [token for token in tokens if token not in STOP_WORDS]

    def get_product(self, product_id):
        return next(
            (product for product in self.products if product.get("id") == product_id),
            None,
        )

    def get_inventory(self, product_id):
        product = self.get_product(product_id)

        if product is None:
            return None

        return {
            "product_id": product_id,
            "inventory": product.get("inventory", 0),
        }


catalog_service = CatalogService()


def search_products(query, limit=None):
    """Search products by title, description, or features."""

    return catalog_service.search(query, limit=limit)


def get_product_details(product_id):
    """Return a single product by id."""

    return catalog_service.get_product(product_id)


def check_inventory(product_id):
    """Return inventory information for a single product."""

    return catalog_service.get_inventory(product_id)
