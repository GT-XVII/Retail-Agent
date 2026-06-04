# Retail Agent

Retail Agent is a proof-of-concept project for building an agentic retail assistant over a structured product catalogue. The current repository is focused on preparing a demo electronics catalogue from the Amazon Reviews 2023 metadata dataset.

The generated catalogue is stored as JSON in `data/electronics_demo_products.json` and is intended to be used by the future LangChain or LangGraph agent layer for product search, comparison, inventory checks, recommendations, and cart actions.

## Current Project Structure

```text
Retail Agent/
├── app/
│   ├── main.py
│   ├── tools/
│   │   ├── product_tools.py
│   │   ├── cart_tools.py
│   │   └── inventory_tools.py
│   ├── services/
│   │   ├── catalog_service.py
│   │   └── cart_service.py
│   └── agent/
│       └── retail_agent.py
├── Dataset Setup/
│   ├── Get_HuggingFace_Dataset.py
│   ├── Build_Demo_Catalog.py
│   └── meta_Electronics.jsonl.gz
├── data/
│   ├── full-00000-of-00010.parquet
│   └── electronics_demo_products.json
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

## Application Layout

The `app` directory contains the initial Retail Agent application skeleton:

* `app/main.py` is the application entry point.
* `app/agent/retail_agent.py` will coordinate the agent workflow.
* `app/services/catalog_service.py` loads and queries the local JSON catalogue with `search_products(query)`, `get_product_details(product_id)`, and `check_inventory(product_id)`.
* `app/services/cart_service.py` manages a prototype in-memory cart with `add_to_cart(product_id, quantity)`, `remove_from_cart(product_id)`, `view_cart()`, and `calculate_total()`.
* `app/tools/product_tools.py`, `app/tools/cart_tools.py`, and `app/tools/inventory_tools.py` are the tool boundaries the future LangChain or LangGraph agent can call.

## API Endpoints

The current FastAPI app exposes:

* `GET /products` returns products, with optional `q` and `limit` query parameters.
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

The test suite is organized as:

```text
tests/
├── api/
│   └── test_main.py
├── unit/
│   ├── test_cart_service.py
│   ├── test_catalog_service.py
│   └── test_tools_and_agent.py
└── conftest.py
```

Coverage currently targets the `app` package and enforces a minimum threshold through `--cov-fail-under`.

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

The demo JSON catalogue contains product records with fields such as:

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

The planned cart model is:

```text
cart
├── user_id
├── product_id
└── quantity
```

## Planned Agent Capabilities

The project is intended to support natural language shopping interactions such as:

* "I need a mechanical keyboard for programming on a Mac."
* "Compare these two monitors and explain which is better for gaming."
* "Show me wireless headphones under 150 with noise cancellation."
* "Add the second option to my cart."
* "What is the total cost of my cart?"

Planned architecture:

```text
User
  ↓
Chat Interface
  ↓
LangChain / LangGraph Agent
  ├── Product Search Tool
  ├── Product Details Tool
  ├── Inventory Tool
  ├── Cart Tool
  └── Recommendation Tool
  ↓
Product Catalogue
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
