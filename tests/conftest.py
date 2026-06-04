import pytest


@pytest.fixture
def sample_products():
    return [
        {
            "id": "keyboard-1",
            "title": "Mechanical Keyboard",
            "brand": "KeysCo",
            "description": "A compact keyboard for programming.",
            "features": "Wireless USB-C backlit keys",
            "price": 99.99,
            "inventory": 7,
        },
        {
            "id": "monitor-1",
            "title": "Gaming Monitor",
            "brand": "DisplayCo",
            "description": "Fast display for gaming.",
            "features": "144 Hz refresh rate",
            "price": 249.5,
            "inventory": 3,
        },
    ]
