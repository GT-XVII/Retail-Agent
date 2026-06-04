from app.agent.retail_agent import RetailAgent
from app.tools import (
    cart_add,
    cart_remove,
    cart_total,
    cart_view,
    inventory_check,
    product_details,
    product_search,
    retail_tools,
)


class FakeCatalogService:
    def __init__(self, product):
        self.product = product

    def search(self, query, limit=None):
        results = [self.product, {"query": query}]

        if limit is None:
            return results

        return results[:limit]

    def get_product(self, product_id):
        return self.product if product_id == self.product["id"] else None

    def get_inventory(self, product_id):
        return {"product_id": product_id, "inventory": self.product["inventory"]}


def test_retail_tools_registry_contains_langchain_tools():
    assert [tool.name for tool in retail_tools] == [
        "product_search",
        "product_details",
        "inventory_check",
        "cart_add",
        "cart_remove",
        "cart_view",
        "cart_total",
    ]


def test_product_tools_invoke_service_functions(monkeypatch, sample_products):
    monkeypatch.setattr(
        "app.tools.product_tools.search_products",
        lambda query, limit=5: sample_products[:limit],
    )
    monkeypatch.setattr(
        "app.tools.product_tools.get_product_details",
        lambda product_id: sample_products[0] if product_id == "keyboard-1" else None,
    )

    assert product_search.invoke({"query": "keyboard", "limit": 1}) == [
        sample_products[0]
    ]
    assert product_details.invoke({"product_id": "keyboard-1"}) == sample_products[0]
    assert product_details.invoke({"product_id": "missing"}) is None


def test_inventory_tool_invokes_service_function(monkeypatch):
    monkeypatch.setattr(
        "app.tools.inventory_tools.check_inventory",
        lambda product_id: {"product_id": product_id, "inventory": 4},
    )

    assert inventory_check.invoke({"product_id": "keyboard-1"}) == {
        "product_id": "keyboard-1",
        "inventory": 4,
    }


def test_cart_tools_invoke_cart_service_functions(monkeypatch):
    monkeypatch.setattr(
        "app.tools.cart_tools.add_to_cart",
        lambda product_id, quantity=1: {"added": product_id, "quantity": quantity},
    )
    monkeypatch.setattr(
        "app.tools.cart_tools.remove_from_cart",
        lambda product_id: {"removed": product_id},
    )
    monkeypatch.setattr(
        "app.tools.cart_tools.view_cart",
        lambda: {"items": [], "total": 0},
    )
    monkeypatch.setattr("app.tools.cart_tools.calculate_total", lambda: 12.5)

    assert cart_add.invoke({"product_id": "keyboard-1", "quantity": 2}) == {
        "added": "keyboard-1",
        "quantity": 2,
    }
    assert cart_remove.invoke({"product_id": "keyboard-1"}) == {
        "removed": "keyboard-1"
    }
    assert cart_view.invoke({}) == {"items": [], "total": 0}
    assert cart_total.invoke({}) == {"total": 12.5}


def test_retail_agent_delegates_to_catalog_service_and_exposes_tools(sample_products):
    product = sample_products[0]
    agent = RetailAgent(catalog_service=FakeCatalogService(product))

    assert agent.get_tools() == retail_tools
    assert agent.search_products("keyboard", limit=1) == [product]
    assert agent.get_product_details("keyboard-1") == product
    assert agent.get_product_details("missing") is None
    assert agent.check_inventory("keyboard-1") == {
        "product_id": "keyboard-1",
        "inventory": 7,
    }
    assert agent.run("hello") == {
        "message": "hello",
        "available_tools": [tool.name for tool in retail_tools],
    }
