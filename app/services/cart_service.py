"""In-memory cart service for the Retail Agent prototype."""

from app.services.catalog_service import get_product_details


cart = {}


def add_to_cart(product_id, quantity):
    """Add a product quantity to the in-memory cart."""

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    product = get_product_details(product_id)

    if product is None:
        raise ValueError(f"Product not found: {product_id}")

    cart[product_id] = cart.get(product_id, 0) + quantity

    return view_cart()


def remove_from_cart(product_id):
    """Remove a product from the in-memory cart."""

    cart.pop(product_id, None)

    return view_cart()


def view_cart():
    """Return cart items with product details and line totals."""

    items = []

    for product_id, quantity in cart.items():
        product = get_product_details(product_id)

        if product is None:
            continue

        price = float(product.get("price", 0))
        items.append(
            {
                "product_id": product_id,
                "title": product.get("title"),
                "price": price,
                "quantity": quantity,
                "line_total": round(price * quantity, 2),
            }
        )

    return {
        "items": items,
        "total": calculate_total(),
    }


def calculate_total():
    """Calculate the current cart total."""

    total = 0

    for product_id, quantity in cart.items():
        product = get_product_details(product_id)

        if product is None:
            continue

        total += float(product.get("price", 0)) * quantity

    return round(total, 2)


class CartService:
    """Manage simple user carts in memory."""

    def __init__(self):
        self.carts = {}

    def add_item(self, user_id, product_id, quantity):
        user_cart = self.carts.setdefault(user_id, {})
        user_cart[product_id] = user_cart.get(product_id, 0) + quantity

        return self.get_cart(user_id)

    def remove_item(self, user_id, product_id):
        cart = self.carts.setdefault(user_id, {})
        cart.pop(product_id, None)

        return self.get_cart(user_id)

    def get_cart(self, user_id):
        return self.carts.get(user_id, {}).copy()
