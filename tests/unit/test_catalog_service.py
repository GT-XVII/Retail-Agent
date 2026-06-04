import json

from app.services import catalog_service as catalog_module
from app.services.catalog_service import CatalogService


def test_catalog_service_loads_products_from_json(tmp_path, sample_products):
    catalog_path = tmp_path / "products.json"
    catalog_path.write_text(json.dumps(sample_products), encoding="utf-8")

    service = CatalogService(catalog_path)

    assert service.products == sample_products


def test_catalog_service_returns_empty_list_when_file_missing(tmp_path):
    service = CatalogService(tmp_path / "missing.json")

    assert service.products == []


def test_catalog_service_searches_title_description_and_features(sample_products):
    service = CatalogService()
    service.products = sample_products

    assert service.search("mechanical") == [sample_products[0]]
    assert service.search("gaming") == [sample_products[1]]
    assert service.search("usb-c") == [sample_products[0]]


def test_catalog_service_empty_search_returns_all_products(sample_products):
    service = CatalogService()
    service.products = sample_products

    assert service.search("") == sample_products


def test_catalog_service_search_applies_limit(sample_products):
    service = CatalogService()
    service.products = sample_products

    assert service.search("", limit=1) == [sample_products[0]]


def test_catalog_service_gets_product_and_inventory(sample_products):
    service = CatalogService()
    service.products = sample_products

    assert service.get_product("keyboard-1") == sample_products[0]
    assert service.get_product("missing") is None
    assert service.get_inventory("keyboard-1") == {
        "product_id": "keyboard-1",
        "inventory": 7,
    }
    assert service.get_inventory("missing") is None


def test_module_level_catalog_functions_use_shared_service(monkeypatch, sample_products):
    service = CatalogService()
    service.products = sample_products
    monkeypatch.setattr(catalog_module, "catalog_service", service)

    assert catalog_module.search_products("monitor", limit=1) == [sample_products[1]]
    assert catalog_module.get_product_details("keyboard-1") == sample_products[0]
    assert catalog_module.check_inventory("monitor-1") == {
        "product_id": "monitor-1",
        "inventory": 3,
    }
