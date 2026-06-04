from typing import Any

from langchain_core.tools import tool

from app.services.cart_service import (
    add_to_cart,
    calculate_total,
    remove_from_cart,
    view_cart,
)


@tool
def cart_add(product_id: str, quantity: int = 1) -> dict[str, Any]:
    """Add a product to the user's shopping cart.

    Use this when the user asks to add, buy, select, or place a product
    into their cart.
    """
    return add_to_cart(product_id=product_id, quantity=quantity)


@tool
def cart_remove(product_id: str) -> dict[str, Any]:
    """Remove a product from the user's shopping cart.

    Use this when the user asks to remove, delete, or take an item out
    of their cart.
    """
    return remove_from_cart(product_id)


@tool
def cart_view() -> dict[str, Any]:
    """View the current shopping cart.

    Use this when the user asks what is in their cart.
    """
    return view_cart()


@tool
def cart_total() -> dict[str, Any]:
    """Calculate the current total cost of the shopping cart.

    Use this when the user asks for the cart total, checkout total,
    subtotal, or total cost.
    """
    return {"total": calculate_total()}
