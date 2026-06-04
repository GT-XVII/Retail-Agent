# Retail Agent

Retail Agent is a proof-of-concept project for building an agentic retail assistant over a structured product catalogue. The current repository includes dataset preparation, a FastAPI backend, a React frontend, normal Python service functions, and LangChain-compatible tools for product, cart, and inventory actions.

The generated catalogue is stored as JSON in `data/electronics_demo_products.json` and is used by the service and tool layers for product search, product details, inventory checks, and cart actions.

## Current Project Structure

```text
Retail Agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── product_tools.py
│   │   ├── cart_tools.py
│   │   └── inventory_tools.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── catalog_service.py
│   │   └── cart_service.py
│   └── agent/
│       ├── __init__.py
│       └── retail_agent.py
├── tests/
│   ├── api/
│   │   └── test_main.py
│   ├── unit/
│   │   ├── test_cart_service.py
│   │   ├── test_catalog_service.py
│   │   └── test_tools_and_agent.py
│   ├── conftest.py
│   └── test_tools.py
├── Dataset Setup/
│   ├── Get_HuggingFace_Dataset.py
│   ├── Build_Demo_Catalog.py
│   └── meta_Electronics.jsonl.gz
├── data/
│   ├── full-00000-of-00010.parquet
│   └── electronics_demo_products.json
├── frontend/
│   ├── src/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── ChatPanel.jsx
│   │       ├── ProductCard.jsx
│   │       └── ProductGrid.jsx
│   ├── package.json
│   └── vite.config.js
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── ReadMe.md
```

## Setup

Create and activate a Python virtual environment from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the packages needed by the dataset scripts:

```bash
pip install -r requirements.txt
```

Install development and test dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the FastAPI application from the project root:

```bash
uvicorn app.main:app --reload
```

Install and run the frontend from the `frontend` directory:

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000` and runs through Vite at `http://localhost:5173`.

## Application Layout

The `app` directory contains the current Retail Agent application:

* `app/main.py` is the application entry point.
* `app/agent/retail_agent.py` coordinates the current tool registry and provides a temporary `run(message)` entry point until the LLM layer is added.
* `app/services/catalog_service.py` loads and queries the local JSON catalogue with `search_products(query)`, `get_product_details(product_id)`, and `check_inventory(product_id)`.
* `app/services/cart_service.py` manages a prototype in-memory cart with `add_to_cart(product_id, quantity)`, `remove_from_cart(product_id)`, `view_cart()`, and `calculate_total()`.
* `app/tools/product_tools.py`, `app/tools/cart_tools.py`, and `app/tools/inventory_tools.py` define LangChain-compatible `@tool` functions.
* `app/tools/__init__.py` exports `retail_tools`, the shared LangChain tool registry.
* `frontend/src/App.jsx` provides the classic store search experience.
* `frontend/src/api.js` calls the FastAPI backend for product search and chat requests.
* `frontend/src/components/ProductGrid.jsx` and `ProductCard.jsx` render catalogue search results.

## Classic Store Search

The frontend search form behaves like a classic store catalogue search:

```text
Search form
  ↓
frontend/src/api.js fetchProducts(query, limit)
  ↓
GET /products?q=...&limit=...
  ↓
search_products(query, limit=limit)
  ↓
CatalogService.search(query, limit=limit)
  ↓
data/electronics_demo_products.json
```

The backend route delegates directly to the normal Python product search function, so the classic store UI and the future LangChain tool layer share the same catalogue search behavior.

## LangChain Tools

The current tool registry exposes:

* `product_search`
* `product_details`
* `inventory_check`
* `cart_add`
* `cart_remove`
* `cart_view`
* `cart_total`

The tools wrap the normal Python service functions, so the business logic can be tested independently from LangChain and reused by FastAPI.

## API Endpoints

The current FastAPI app exposes:

* `GET /products` returns classic catalogue search results, with optional `q` and `limit` query parameters.
* `GET /products/{id}` returns product details for one product.
* `POST /cart/add` adds an item to the in-memory cart.
* `GET /cart` returns cart contents and total cost.
* `POST /chat` accepts a message and returns basic catalogue search results until the LangChain agent is added.

## Tests

Automated tests are built with `pytest` and coverage is configured in `pyproject.toml`.

Run the full test suite with one command:

```bash
pytest
```

Run frontend checks from the `frontend` directory:

```bash
npm run lint
npm run build
```

The test suite is organized as:

```text
tests/
├── api/
│   └── test_main.py
├── test_tools.py
├── unit/
│   ├── test_cart_service.py
│   ├── test_catalog_service.py
│   └── test_tools_and_agent.py
└── conftest.py
```

Coverage currently targets the `app` package and enforces a minimum threshold through `--cov-fail-under`. The latest verified backend run passed with 28 tests and 100% coverage. The frontend lint and production build also pass.

## Building the Demo Catalogue

Run the setup scripts from inside the `Dataset Setup` directory. The scripts use relative paths that write into the project-level `data` directory.

```bash
cd "Dataset Setup"
python Get_HuggingFace_Dataset.py
python Build_Demo_Catalog.py
```

`Get_HuggingFace_Dataset.py` downloads the initial Amazon Reviews 2023 Electronics metadata parquet file from Hugging Face and copies it to:

```text
data/full-00000-of-00010.parquet
```

`Build_Demo_Catalog.py` reads that parquet dataset, filters and normalizes product records, adds demo inventory values, and writes the final JSON catalogue to:

```text
data/electronics_demo_products.json
```

## Product Data Model

The demo JSON catalogue is built from the Amazon Reviews 2023 Electronics metadata parquet file. `Build_Demo_Catalog.py` filters and normalizes source records into product objects shaped like:

```text
product
├── id
├── title
├── brand
├── category
├── categories
├── description
├── features
├── price
├── average_rating
├── rating_number
├── image_url
└── inventory
```

The current cart is in-memory only and is keyed by `product_id` internally:

```text
cart
└── product_id: quantity
```

`view_cart()` and `GET /cart` return the cart as enriched line items with a calculated total:

```text
cart_response
├── items
│   └── item
│       ├── product_id
│       ├── title
│       ├── price
│       ├── quantity
│       └── line_total
└── total
```

## Planned Agent Capabilities

The project currently has the service and LangChain tool layer needed for product search, product details, inventory checks, cart changes, cart viewing, and cart totals. `RetailAgent` exposes the shared `retail_tools` registry and has a temporary `run(message)` method that returns available tool names until an LLM is wired in.

Current tool-backed capabilities:

* Search the catalogue through the classic store UI and `GET /products`.
* Search the catalogue through the LangChain `product_search` tool.
* Retrieve a product by ID with `product_details`.
* Check inventory with `inventory_check`.
* Add and remove products with `cart_add` and `cart_remove`.
* View the cart and total with `cart_view` and `cart_total`.

The intended conversational layer will route natural language requests to these tools, enabling interactions such as:

* "I need a mechanical keyboard for programming on a Mac."
* "Show me wireless headphones under 150 with noise cancellation."
* "Is this product in stock?"
* "Add this keyboard to my cart."
* "What is the total cost of my cart?"

Current architecture:

```text
User
  ↓
React Frontend / FastAPI
  ↓
Classic Search Route / RetailAgent
  ↓
Catalog Service / LangChain Tool Registry
  ├── product_search
  ├── product_details
  ├── inventory_check
  ├── cart_add
  ├── cart_remove
  ├── cart_view
  └── cart_total
  ↓
Python Services
  ├── CatalogService
  └── In-Memory Cart
  ↓
JSON Product Catalogue
```

## Planned Technology Stack

* Python
* LangChain / LangGraph
* Structured JSON product catalogue
* PostgreSQL
* Docker
* Kubernetes
* Amazon Reviews 2023 product metadata subset

## Future Enhancements

* Build the conversational agent layer.
* Add product search and recommendation tools.
* Add persistent cart and user session storage.
* Move catalogue storage from JSON to PostgreSQL.
* Add Docker and Kubernetes deployment manifests.
* Add monitoring and observability with Prometheus and Grafana.
