import pytest

from app.services import cart_service


@pytest.fixture(autouse=True)
def empty_cart():
    cart_service.cart.clear()
    yield
    cart_service.cart.clear()


def test_add_to_cart_adds_and_accumulates_quantity(monkeypatch, sample_products):
    monkeypatch.setattr(
        cart_service,
        "get_product_details",
        lambda product_id: sample_products[0],
    )

    cart_service.add_to_cart("keyboard-1", 1)
    result = cart_service.add_to_cart("keyboard-1", 2)

    assert result == {
        "items": [
            {
                "product_id": "keyboard-1",
                "title": "Mechanical Keyboard",
                "price": 99.99,
                "quantity": 3,
                "line_total": 299.97,
            }
        ],
        "total": 299.97,
    }


def test_add_to_cart_rejects_invalid_quantity():
    with pytest.raises(ValueError, match="Quantity must be greater than zero"):
        cart_service.add_to_cart("keyboard-1", 0)


def test_add_to_cart_rejects_missing_product(monkeypatch):
    monkeypatch.setattr(cart_service, "get_product_details", lambda product_id: None)

    with pytest.raises(ValueError, match="Product not found: missing"):
        cart_service.add_to_cart("missing", 1)


def test_remove_from_cart_removes_existing_and_ignores_missing(monkeypatch, sample_products):
    monkeypatch.setattr(
        cart_service,
        "get_product_details",
        lambda product_id: sample_products[0],
    )

    cart_service.add_to_cart("keyboard-1", 1)

    assert cart_service.remove_from_cart("keyboard-1") == {"items": [], "total": 0}
    assert cart_service.remove_from_cart("missing") == {"items": [], "total": 0}


def test_view_cart_skips_products_that_no_longer_exist(monkeypatch):
    cart_service.cart["missing"] = 2
    monkeypatch.setattr(cart_service, "get_product_details", lambda product_id: None)

    assert cart_service.view_cart() == {"items": [], "total": 0}
    assert cart_service.calculate_total() == 0


def test_cart_service_class_manages_user_carts():
    service = cart_service.CartService()

    assert service.add_item("user-1", "keyboard-1", 2) == {"keyboard-1": 2}
    assert service.add_item("user-1", "keyboard-1", 1) == {"keyboard-1": 3}
    assert service.get_cart("user-2") == {}
    assert service.remove_item("user-1", "keyboard-1") == {}
    assert service.remove_item("user-1", "missing") == {}
