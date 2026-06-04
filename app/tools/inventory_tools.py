from langchain_core.tools import tool

from app.services.catalog_service import check_inventory


@tool
def inventory_check(product_id: str) -> dict:
    """Check whether a product is currently available in inventory.

    Use this before adding a product to the cart or when the user asks
    whether an item is in stock.
    """
    return check_inventory(product_id)