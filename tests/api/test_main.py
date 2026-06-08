from fastapi.testclient import TestClient

from app.errors import AgentExecutionError
from app.main import app, main
from app.services import cart_service


class FakeCatalog:
    def __init__(self, products):
        self.products = products

    def search(self, query, limit=None):
        if not query:
            results = self.products
        else:
            query = query.lower()

            results = [
                product
                for product in self.products
                if query in product["title"].lower()
                or query in product["description"].lower()
                or query in product["features"].lower()
            ]

        if limit is None:
            return results

        return results[:limit]

    def get_product(self, product_id):
        return next(
            (product for product in self.products if product["id"] == product_id),
            None,
        )


def test_main_prints_run_command(capsys):
    main()

    assert "uvicorn app.main:app --reload" in capsys.readouterr().out


def test_products_endpoint_returns_limited_results(monkeypatch, sample_products):
    calls = []

    def search(query, limit=None):
        calls.append({"query": query, "limit": limit})
        return FakeCatalog(sample_products).search(query, limit=limit)

    monkeypatch.setattr(
        "app.main.search_products",
        search,
    )
    client = TestClient(app)

    response = client.get("/products?limit=1")

    assert response.status_code == 200
    assert calls == [{"query": "", "limit": 1}]
    assert response.json()["count"] == 1
    assert response.json()["products"] == [sample_products[0]]


def test_products_endpoint_filters_by_query(monkeypatch, sample_products):
    calls = []

    def search(query, limit=None):
        calls.append({"query": query, "limit": limit})
        return FakeCatalog(sample_products).search(query, limit=limit)

    monkeypatch.setattr(
        "app.main.search_products",
        search,
    )
    client = TestClient(app)

    response = client.get("/products?q=monitor")

    assert response.status_code == 200
    assert calls == [{"query": "monitor", "limit": 25}]
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


def test_cart_remove_endpoint_removes_item(monkeypatch, sample_products):
    cart_service.cart.clear()
    cart_service.cart["keyboard-1"] = 1
    monkeypatch.setattr(
        "app.services.cart_service.get_product_details",
        FakeCatalog(sample_products).get_product,
    )
    client = TestClient(app)

    response = client.post(
        "/cart/remove",
        json={"product_id": "keyboard-1"},
    )

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}

    cart_service.cart.clear()


def test_chat_endpoint_returns_basic_search_matches(monkeypatch, sample_products):
    class FakeUserChatService:
        def __init__(self):
            self.calls = []

        def send_message(self, request):
            self.calls.append(request)

            return {
                "message": f"answered {request.message}",
                "user_id": request.user_id,
                "conversation_id": request.conversation_id,
                "history": [
                    {"role": "user", "content": request.message},
                    {"role": "assistant", "content": f"answered {request.message}"},
                ],
            }

    fake_chat_service = FakeUserChatService()
    monkeypatch.setattr("app.main.user_chat_service", fake_chat_service)
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={
            "message": "keyboard",
            "user_id": "user-1",
            "conversation_id": "conversation-1",
        },
    )

    assert response.status_code == 200
    assert fake_chat_service.calls[0].message == "keyboard"
    assert response.json() == {
        "message": "answered keyboard",
        "user_id": "user-1",
        "conversation_id": "conversation-1",
        "history": [
            {"role": "user", "content": "keyboard"},
            {"role": "assistant", "content": "answered keyboard"},
        ],
    }


def test_chat_endpoint_returns_structured_agent_errors(monkeypatch):
    class FailingUserChatService:
        def send_message(self, request):
            raise AgentExecutionError(
                "Agent failed while calling the model.",
                details={"type": "RuntimeError", "message": "upstream timeout"},
            )

    monkeypatch.setattr("app.main.user_chat_service", FailingUserChatService())
    client = TestClient(app)

    response = client.post("/chat", json={"message": "keyboard"})

    assert response.status_code == 502
    assert response.json() == {
        "error": {
            "code": "agent_execution_error",
            "message": "Agent failed while calling the model.",
            "details": {"type": "RuntimeError", "message": "upstream timeout"},
        }
    }
