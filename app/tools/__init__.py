"""Agent tool package."""

from app.tools.cart_tools import cart_add, cart_remove, cart_total, cart_view
from app.tools.inventory_tools import inventory_check
from app.tools.product_tools import product_details, product_search


retail_tools = [
    product_search,
    product_details,
    inventory_check,
    cart_add,
    cart_remove,
    cart_view,
    cart_total,
]