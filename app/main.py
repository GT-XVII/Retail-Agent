"""FastAPI entry point for the Retail Agent prototype."""

import sys
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

if __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.cart_service import add_to_cart, view_cart
from app.services.catalog_service import get_product_details, search_products


app = FastAPI(title="Retail Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AddToCartRequest(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


class ChatRequest(BaseModel):
    message: str


@app.get("/products")
def products(q: str = "", limit: int = 25):
    results = search_products(q, limit=limit)

    return {
        "count": len(results),
        "products": results,
    }


@app.get("/products/{product_id}")
def product_details(product_id: str):
    product = get_product_details(product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found.")

    return product


@app.post("/cart/add")
def cart_add(request: AddToCartRequest):
    try:
        return add_to_cart(request.product_id, request.quantity)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/cart")
def cart():
    return view_cart()


@app.post("/chat")
def chat(request: ChatRequest):
    matches = search_products(request.message, limit=5)

    return {
        "message": "LangChain is not wired in yet. Returning catalog matches from the Python search function.",
        "query": request.message,
        "products": matches,
    }


def main():
    """Print the local development command."""

    print("Run the API with: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
