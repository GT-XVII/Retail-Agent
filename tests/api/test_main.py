from fastapi.testclient import TestClient

from app.main import app, main
from app.services import cart_service


class FakeCatalog:
    def __init__(self, products):
        self.products = products

    def search(self, query):
        if not query:
            return self.products

        query = query.lower()

        return [
            product
            for product in self.products
            if query in product["title"].lower()
            or query in product["description"].lower()
            or query in product["features"].lower()
        ]

    def get_product(self, product_id):
        return next(
            (product for product in self.products if product["id"] == product_id),
            None,
        )


def test_main_prints_run_command(capsys):
    main()

    assert "uvicorn app.main:app --reload" in capsys.readouterr().out


def test_products_endpoint_returns_limited_results(monkeypatch, sample_products):
    monkeypatch.setattr(
        "app.main.search_products",
        FakeCatalog(sample_products).search,
    )
    client = TestClient(app)

    response = client.get("/products?limit=1")

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert response.json()["products"] == [sample_products[0]]


def test_products_endpoint_filters_by_query(monkeypatch, sample_products):
    monkeypatch.setattr(
        "app.main.search_products",
        FakeCatalog(sample_products).search,
    )
    client = TestClient(app)

    response = client.get("/products?q=monitor")

    assert response.status_code == 200
    assert response.json()["products"] == [sample_products[1]]


def test_product_details_endpoint_returns_product(monkeypatch, sample_products):
    monkeypatch.setattr(
        "app.main.get_product_details",
        FakeCatalog(sample_products).get_product,
    )
    client = TestClient(app)

    response = client.get("/products/keyboard-1")

    assert response.status_code == 200
    assert response.json() == sample_products[0]


def test_product_details_endpoint_returns_404(monkeypatch, sample_products):
    monkeypatch.setattr(
        "app.main.get_product_details",
        FakeCatalog(sample_products).get_product,
    )
    client = TestClient(app)

    response = client.get("/products/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found."}


def test_cart_add_endpoint_returns_cart(monkeypatch, sample_products):
    cart_service.cart.clear()
    monkeypatch.setattr(
        "app.services.cart_service.get_product_details",
        FakeCatalog(sample_products).get_product,
    )
    client = TestClient(app)

    response = client.post(
        "/cart/add",
        json={"product_id": "keyboard-1", "quantity": 2},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 199.98

    cart_service.cart.clear()


def test_cart_add_endpoint_returns_400_for_missing_product(monkeypatch, sample_products):
    monkeypatch.setattr(
        "app.services.cart_service.get_product_details",
        FakeCatalog(sample_products).get_product,
    )
    client = TestClient(app)

    response = client.post(
        "/cart/add",
        json={"product_id": "missing", "quantity": 1},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Product not found: missing"}


def test_cart_endpoint_returns_current_cart(monkeypatch, sample_products):
    cart_service.cart.clear()
    cart_service.cart["monitor-1"] = 1
    monkeypatch.setattr(
        "app.services.cart_service.get_product_details",
        FakeCatalog(sample_products).get_product,
    )
    client = TestClient(app)

    response = client.get("/cart")

    assert response.status_code == 200
    assert response.json()["total"] == 249.5

    cart_service.cart.clear()


def test_chat_endpoint_returns_basic_search_matches(monkeypatch, sample_products):
    monkeypatch.setattr(
        "app.main.search_products",
        FakeCatalog(sample_products).search,
    )
    client = TestClient(app)

    response = client.post("/chat", json={"message": "keyboard"})

    assert response.status_code == 200
    assert response.json()["query"] == "keyboard"
    assert response.json()["products"] == [sample_products[0]]
