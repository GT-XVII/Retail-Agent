"""Retail Agent orchestration placeholder."""

from app.services.cart_service import CartService
from app.services.catalog_service import CatalogService


class RetailAgent:
    """Coordinate catalog and cart services for future agent workflows."""

    def __init__(self, catalog_service=None, cart_service=None):
        self.catalog_service = catalog_service or CatalogService()
        self.cart_service = cart_service or CartService()

    def search_products(self, query):
        return self.catalog_service.search(query)

    def get_product_details(self, product_id):
        return self.catalog_service.get_product(product_id)

    def check_inventory(self, product_id):
        return self.catalog_service.get_inventory(product_id)
