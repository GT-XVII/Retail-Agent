"""
Builds a simplified product catalog from the Amazon Electronics parquet dataset.

The script loads the source dataset, filters out incomplete or low-quality
records, normalizes fields into a JSON-friendly structure, generates a small
inventory value for demo purposes, and exports the resulting catalog as a
single JSON file for use by the Retail Agent application.
"""

import json
import random
import re
from pathlib import Path

import pandas as pd


INPUT_FILE = Path("../data/full-00000-of-00010.parquet")
OUTPUT_FILE = Path("../data/electronics_demo_products.json")


# Price normalization helpers.
# Converts raw dataset price values into numeric floats.
def clean_price(value):
    """Convert price strings into floats."""

    if value is None:
        return None

    value = str(value)

    if value.lower() in ["none", "nan"]:
        return None

    match = re.search(r"\d+(\.\d+)?", value.replace(",", ""))

    if not match:
        return None

    return float(match.group())


# Text processing helpers.
# Flattens list-based dataset fields into readable strings.
def join_text(value):
    """Convert list-like fields into a single string."""

    if value is None:
        return ""

    if hasattr(value, "tolist"):
        value = value.tolist()

    if isinstance(value, list):
        return " ".join(str(v) for v in value if v is not None)

    return str(value)


# JSON conversion helpers.
# Ensures category and metadata fields are stored as string lists.
def to_json_list(value):
    """Convert list-like values into a JSON-safe list of strings."""

    if value is None:
        return []

    if hasattr(value, "tolist"):
        value = value.tolist()

    if isinstance(value, list):
        return [str(v) for v in value if v is not None]

    return [str(value)]


# Image extraction helpers.
# Selects the best available image URL from the dataset record.
def get_image(images):
    """Return the first usable image URL."""

    if images is None:
        return None

    if hasattr(images, "tolist"):
        images = images.tolist()

    if not isinstance(images, dict):
        return None

    for size in ["hi_res", "large", "thumb"]:
        values = images.get(size)

        if hasattr(values, "tolist"):
            values = values.tolist()

        if values is None:
            continue

        for url in values:
            if url:
                return url

    return None


# Main catalog generation workflow.
# Loads the parquet dataset, applies quality filters, transforms records,
# and exports the final demo catalog to JSON.
def build_catalog():
    print(f"Loading parquet file from {INPUT_FILE.resolve()}...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Could not find input file: {INPUT_FILE.resolve()}")

    df = pd.read_parquet(INPUT_FILE)

    print(f"Loaded {len(df):,} rows")

    products = []

    for _, row in df.iterrows():

        description = join_text(row.get("description"))
        features = join_text(row.get("features"))
        price = clean_price(row.get("price"))

        if not row.get("title"):
            continue

        if price is None:
            continue

        if len(description + features) < 150:
            continue

        if row.get("rating_number", 0) < 20:
            continue

        product = {
            "id": row.get("parent_asin"),
            "title": row.get("title"),
            "brand": row.get("store"),
            "category": row.get("main_category"),
            "categories": to_json_list(row.get("categories")),
            "description": description,
            "features": join_text(row.get("features")),
            "price": price,
            "average_rating": float(row.get("average_rating")),
            "rating_number": int(row.get("rating_number")),
            "image_url": get_image(row.get("images")),
            "inventory": random.randint(0, 50),
        }

        products.append(product)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(products):,} valid products to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_catalog()