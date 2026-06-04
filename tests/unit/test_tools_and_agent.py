from app.agent.retail_agent import RetailAgent
from app.services.cart_service import (
    add_to_cart,
    calculate_total,
    remove_from_cart,
    view_cart,
)
from app.services.catalog_service import (
    check_inventory,
    get_product_details,
    search_products,
)
from app.tools import cart_tools, inventory_tools, product_tools


class FakeCatalogService:
    def __init__(self, product):
        self.product = product

    def search(self, query):
        return [self.product, query]

    def get_product(self, product_id):
        return self.product if product_id == self.product["id"] else None

    def get_inventory(self, product_id):
        return {"product_id": product_id, "inventory": self.product["inventory"]}


def test_tool_modules_re_export_service_functions():
    assert product_tools.search_products is search_products
    assert product_tools.get_product_details is get_product_details
    assert product_tools.check_inventory is check_inventory
    assert inventory_tools.check_inventory is check_inventory
    assert cart_tools.add_to_cart is add_to_cart
    assert cart_tools.remove_from_cart is remove_from_cart
    assert cart_tools.view_cart is view_cart
    assert cart_tools.calculate_total is calculate_total


def test_retail_agent_delegates_to_catalog_service(sample_products):
    product = sample_products[0]
    agent = RetailAgent(catalog_service=FakeCatalogService(product))

    assert agent.search_products("keyboard") == [product, "keyboard"]
    assert agent.get_product_details("keyboard-1") == product
    assert agent.get_product_details("missing") is None
    assert agent.check_inventory("keyboard-1") == {
        "product_id": "keyboard-1",
        "inventory": 7,
    }
