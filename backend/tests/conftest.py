"""
Shared fixtures.

Unit tests run anywhere. Database tests need a *separate, disposable*
Postgres database, because they drop and recreate every table:

    createdb wheyscan_test
    TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/wheyscan_test pytest

Without TEST_DATABASE_URL the database tests are skipped.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pytest

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

# app.core.config needs DATABASE_URL at import time; never let tests fall
# back to the developer's real database from backend/.env.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL or "postgresql+psycopg://unused/unused"

from app.ingestion.scraper.base.types import RawProduct  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


# ----------------------------------------------------------------------
# Optimum Nutrition: real Shopify product JSON, served by a fake client
# ----------------------------------------------------------------------

@pytest.fixture(scope="session")
def on_products() -> dict:
    return json.loads((FIXTURES / "optimum_nutrition_products.json").read_text())


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class FakeShopifyClient:
    def __init__(self, products: dict):
        self.products = products

    def get(self, url, **kwargs):
        return FakeResponse(self.products[url.removesuffix(".json")])


@pytest.fixture
def on_client(on_products) -> FakeShopifyClient:
    return FakeShopifyClient(on_products)


# ----------------------------------------------------------------------
# HealthKart: RawProducts shaped like VeronicaParser output
# ----------------------------------------------------------------------

def healthkart_raw(rid, name, brand, weight, flavour, protein_type, price, url):
    return RawProduct(
        retailer="healthkart",
        retailer_product_id=rid,
        name=name,
        brand=brand,
        weight=weight,
        flavour=flavour,
        protein_type=protein_type,
        current_price=price,
        original_price=None,
        discount=None,
        product_url=url,
        image_url=None,
        availability="In Stock",
        rating=None,
        review_count=None,
        scraped_at=datetime(2026, 9, 23, 10, 0, 0),
    )


@pytest.fixture
def healthkart_products() -> list[RawProduct]:
    base = "https://www.healthkart.com"
    return [
        healthkart_raw("84971", "MuscleBlaze Biozyme Performance Whey", "MuscleBlaze",
                       "1 kg", "Rich Chocolate", "Whey Blend", 3999.0,
                       f"{base}/muscleblaze-biozyme-performance-whey/SP-84971"),
        healthkart_raw("137613", "Ronnie Coleman Pro-Antium Whey Protein", "Ronnie Coleman",
                       "2 lb", "Chocolate", "Whey Blend", 3199.0,
                       f"{base}/ronnie-coleman-pro-antium-whey-protein/SP-137613"),
        healthkart_raw("129175", "MuscleBlaze Biozyme Gold 100% Whey", "MuscleBlaze",
                       "1 kg", "Rich Milk Chocolate", "Whey Isolate", 4599.0,
                       f"{base}/muscleblaze-biozyme-gold-100-whey/SP-129175"),
        healthkart_raw("121273", "MuscleBlaze Biozyme Whey PR", "MuscleBlaze",
                       "1 kg", "Rich Chocolate", "Whey Blend", 3949.0,
                       f"{base}/muscleblaze-biozyme-whey-pr/SP-121273"),
        healthkart_raw("143771", "Optimum Nutrition Gold Standard 100% Whey Protein", "ON",
                       "2 lb", "Double Rich Chocolate", "Whey Blend", 4999.0,
                       f"{base}/on-optimum-nutrition-gold-standard-100-whey-protein/SP-143771"),
    ]


# ----------------------------------------------------------------------
# Database
# ----------------------------------------------------------------------

@pytest.fixture
def db():
    if not TEST_DATABASE_URL:
        pytest.skip("set TEST_DATABASE_URL to run database tests")

    from sqlalchemy import create_engine
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.orm import sessionmaker

    import app.db.models  # noqa: F401
    from app.db.base import Base

    engine = create_engine(TEST_DATABASE_URL)

    try:
        Base.metadata.drop_all(engine)
    except OperationalError as exc:
        pytest.skip(f"test database unreachable: {exc}")

    Base.metadata.create_all(engine)

    session = sessionmaker(bind=engine, autoflush=False)()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()
