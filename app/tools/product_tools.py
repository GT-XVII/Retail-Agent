from typing import Any

from langchain_core.tools import tool

from app.services.catalog_service import get_product_details, search_products


@tool
def product_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search the product catalogue using a natural language query.

    Use this when the user is looking for products, comparing options,
    or asking for products matching a need such as headphones, keyboards,
    monitors, accessories, or budget constraints.
    """
    return search_products(query=query, limit=limit)


@tool
def product_details(product_id: str) -> dict[str, Any] | None:
    """Get full product details for a specific product ID.

    Use this when the user asks about a known product, wants more detail,
    or refers to a product returned by product_search.
    """
    return get_product_details(product_id)