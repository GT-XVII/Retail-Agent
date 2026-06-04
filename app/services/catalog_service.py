"""Catalog data access service for the Retail Agent."""

import json
from pathlib import Path


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
        query = query.lower()

        if not query:
            results = self.products
        else:
            results = [
                product
                for product in self.products
                if query in product.get("title", "").lower()
                or query in product.get("description", "").lower()
                or query in product.get("features", "").lower()
            ]

        if limit is None:
            return results

        return results[:limit]

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
