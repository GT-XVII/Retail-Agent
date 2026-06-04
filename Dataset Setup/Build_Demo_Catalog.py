"""
Builds a simplified product catalog from the Amazon Electronics parquet dataset.

The script loads the source dataset, filters out incomplete or low-quality
records, normalizes fields into a JSON-friendly structure, generates a small
inventory value for demo purposes, and exports the resulting catalog as a
single JSON file for use by the Retail Agent application.
"""

import json
import math
import random
import re
from pathlib import Path

import pandas as pd


INPUT_FILE = Path("../data/full-00000-of-00010.parquet")
OUTPUT_FILE = Path("../data/electronics_demo_products.json")


# Missing value helpers.
# Handles None, pandas NaN, numpy NaN, and float NaN consistently.
def is_missing(value):
    """Return True when a dataset value is missing or NaN."""

    if value is None:
        return True

    if isinstance(value, float) and math.isnan(value):
        return True

    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def to_json_scalar(value):
    """Convert a single dataset value into a JSON-safe scalar."""

    if is_missing(value):
        return None

    return value


def to_json_string(value):
    """Convert a single dataset value into a JSON-safe string."""

    if is_missing(value):
        return None

    return str(value)


def clean_json_value(value):
    """Recursively convert NaN values into None before JSON export."""

    if is_missing(value):
        return None

    if isinstance(value, dict):
        return {key: clean_json_value(item) for key, item in value.items()}

    if isinstance(value, list):
        return [clean_json_value(item) for item in value]

    return value


# Category normalization helpers.
# Uses the most specific category from the category path when main_category is missing.
def derive_category(category, categories):
    """Return the main category or fall back to the most specific category path entry."""

    if not is_missing(category):
        return str(category)

    category_list = to_json_list(categories)

    if category_list:
        return category_list[-1]

    return None


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

    if is_missing(value):
        return []

    if hasattr(value, "tolist"):
        value = value.tolist()

    if isinstance(value, list):
        return [str(v) for v in value if not is_missing(v)]

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

        if is_missing(row.get("rating_number")) or row.get("rating_number", 0) < 20:
            continue

        categories = to_json_list(row.get("categories"))

        product = {
            "id": to_json_string(row.get("parent_asin")),
            "title": to_json_string(row.get("title")),
            "brand": to_json_string(row.get("store")),
            "category": derive_category(row.get("main_category"), categories),
            "categories": categories,
            "description": description,
            "features": features,
            "price": price,
            "average_rating": float(row.get("average_rating")),
            "rating_number": int(row.get("rating_number")),
            "image_url": to_json_string(get_image(row.get("images"))),
            "inventory": random.randint(0, 50),
        }

        products.append(clean_json_value(product))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False, allow_nan=False)

    print(f"Saved {len(products):,} valid products to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_catalog()