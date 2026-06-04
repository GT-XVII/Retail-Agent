"""Retail Agent orchestration placeholder."""

from app.services.cart_service import CartService
from app.services.catalog_service import CatalogService
from app.tools import retail_tools


class RetailAgent:
    """Coordinate catalog, cart, and LangChain tools for agent workflows."""

    def __init__(self, catalog_service=None, cart_service=None):
        self.catalog_service = catalog_service or CatalogService()
        self.cart_service = cart_service or CartService()
        self.tools = retail_tools

    def get_tools(self):
        """Return the LangChain tools available to the agent."""
        return self.tools

    def search_products(self, query, limit=None):
        return self.catalog_service.search(query, limit=limit)

    def get_product_details(self, product_id):
        return self.catalog_service.get_product(product_id)

    def check_inventory(self, product_id):
        return self.catalog_service.get_inventory(product_id)

    def run(self, message):
        """Temporary agent entry point until the LLM layer is added."""
        return {
            "message": message,
            "available_tools": [tool.name for tool in self.tools],
        }
